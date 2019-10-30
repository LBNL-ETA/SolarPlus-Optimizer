import time
from pyxbos.process import XBOSProcess, b64decode, b64encode, schedule, run_loop
from pyxbos import xbos_pb2
from pyxbos import flexstat_pb2
from pyxbos import nullabletypes_pb2 as types
from datetime import datetime
from functools import partial
from collections import deque
import asyncio

class FlexstatDriver(XBOSProcess):
	def __init__(self, cfg):
		super().__init__(cfg)
		self.namespace = b64decode(cfg['namespace'])
		self.base_resource = cfg['base_resource']
		self._rate = cfg['publish_rate']
		self._set_setpoint_rate = cfg["check_setpoint_rate"]
		self.service_name_map = cfg['service_name_map']
		self.thermostat_config = cfg['thermostat_config']

		self.bacnet_mask = self.thermostat_config.get('bacnet_network_mask')
		self.bacnet_router_address = self.thermostat_config.get('bacnet_router_address', None)
		self.bbmd_ttl = self.thermostat_config.get('bbmd_ttl', None)

		self._default_time_threshold = self.thermostat_config.get("default_time_threshold", 60)
		self._default_heating_setpoint = self.thermostat_config.get("default_heating_setpoint", 67)
		self._default_cooling_setpoint = self.thermostat_config.get("default_cooling_setpoint", 74)

		self.init_thermostats()

		self._setpoints = {}
		self._actuation_message_uri = self.base_resource+"/*/actuation"
		self._actuation_message_path = ".flexstatActuationMessage.setpoints"

		# Check message bus and extract latest setpoint list
		schedule(self._query_existing(uri=self._actuation_message_uri))

		# set subscription to any new action message that is published and extract setpoint list
		schedule(
			self.subscribe_extract(self.namespace, self._actuation_message_uri, self._actuation_message_path,
								   self._save_setpoints, "save_setpoints"))

		# read thermostat points every _rate seconds and publish
		schedule(self.call_periodic(self._rate, self._read_and_publish, runfirst=True))

		# periodically check if there is a need to change setpoints
		schedule(self.call_periodic(self._set_setpoint_rate, self._set_setpoints, runfirst=False))


	def init_thermostats(self):
		if self.bacnet_router_address == None or self.bbmd_ttl == None:
			self.bacnet = BAC0.connect(ip=self.bacnet_mask)
		else:
			self.bacnet = BAC0.connect(ip=self.bacnet_mask, bbmdAddress=self.bacnet_router_address, bbmdTTL=self.bbmd_ttl)
		self.point_map = self.thermostat_config['point_map']

		self.device_map = {}
		for service_name in self.service_name_map:
			ip = self.service_name_map[service_name].get('ip')
			device_id = self.service_name_map[service_name].get('device_id', 1)

			device = BAC0.device(address=ip, device_id=device_id, network=self.bacnet)
			self.device_map[service_name] = device


	def extract_setpoint_dict(self, setpoint_values):
		'''
            Example setpoints:
            {
                'test_tstat2': {
                    1571944506.1637542: {
                        'heating_setpoint': 20.2,
                        'cooling_setpoint': 30.5
                    },
                    1571944566.1637542: {
                        'heating_setpoint': 30.2,
                        'cooling_setpoint': 40.5
                    },
                    1571944626.1637542: {
                        'heating_setpoint': 40.2,
                        'cooling_setpoint': 50.5
                    },
                    1571944686.1637542: {
                        'heating_setpoint': 50.2,
                        'cooling_setpoint': 60.5
                    },
                    1571944746.1637542: {
                        'heating_setpoint': 60.2,
                        'cooling_setpoint': 70.5
                    }
                }
            }
        '''
		setpoint_dict = {}
		for setpoint in setpoint_values:
			time = float(setpoint['changeTime'])/1e9
			setpoint_dict[time] = {}

			if 'heatingSetpoint' in setpoint.keys():
				setpoint_dict[time]['heating_setpoint'] = setpoint['heatingSetpoint'].get('value', None)

			if 'coolingSetpoint' in setpoint.keys():
				setpoint_dict[time]['cooling_setpoint'] = setpoint['coolingSetpoint'].get('value', None)
		return setpoint_dict

	async def _query_existing(self, uri):
		responses = await self.query_topic(self.namespace, uri, self._actuation_message_path)
		for response in responses:
			device = response.uri.split("/")[1]
			setpoint_dict = self.extract_setpoint_dict(setpoint_values=response.values[0])
			if not device in self._setpoints.keys():
				self._setpoints[device] = setpoint_dict
		await self._set_setpoints()

	def _save_setpoints(self, resp):
		device = resp.uri.split('-')[-1].split("/")[1]
		setpoint_dict = self.extract_setpoint_dict(setpoint_values=resp.values[0])
		self._setpoints[device] = setpoint_dict

	async def _set_setpoints(self, *args):
		time_now = time.time()
		device_setpoint_dict = self._setpoints
		for device in device_setpoint_dict:
			found = False
			setpoint_dict = device_setpoint_dict[device]
			
			for change_time in sorted(setpoint_dict, reverse=True):
				if not found and time_now > change_time:
					found = True
					if (time_now - change_time) > self._default_time_threshold:
						# CASE1: if time_now is at least an hour ahead of the last setpoint in the list of setpoints, set to default setpoints
						heating_setpoint = self._default_heating_setpoint
						cooling_setpoint = self._default_cooling_setpoint
					else:
						# CASE2: if time_now is between the list of setpoints, get the new setpoints
						heating_setpoint = setpoint_dict[change_time].get('heating_setpoint', None)
						cooling_setpoint = setpoint_dict[change_time].get('cooling_setpoint', None)
			
			if not found:
				first_change_time = sorted(setpoint_dict)[0]
				if (first_change_time - time_now) > self._default_time_threshold:
					# CASE3: if the tiem_now is more than 1 hour before the 1st setpoint in the list of setpoints; set default setpoints
					heating_setpoint = self._default_heating_setpoint
					cooling_setpoint = self._default_cooling_setpoint
				else:
					# CASE4: if the tiem_now is less than 1 hour before the 1st setpoint in the list of setpoints; do not change anything
					heating_setpoint = None
					cooling_setpoint = None
			
			# TODO: find what variables to change
			self.change_setpoints(device=device, variable_name='heating_setpoint', new_value=heating_setpoint)
			self.change_setpoints(device=device, variable_name='cooling_setpoint', new_value=cooling_setpoint)

	def change_setpoints(self, device, variable_name, new_value):
		if new_value!=None:
			# TODO: remove during deployment
			if variable_name == 'heating_setpoint':

				occ_hsp_bacnet_variable_name = self.point_map['occ_heating_setpt']
				current_occ_heating_sp = self.device_map[device][occ_hsp_bacnet_variable_name].value

				unocc_hsp_bacnet_variable_name = self.point_map['unocc_heating_setpt']
				current_unocc_heating_sp = self.device_map[device][unocc_hsp_bacnet_variable_name].value

				if current_occ_heating_sp != new_value or current_unocc_heating_sp != new_value:
					self.device_map[device][occ_hsp_bacnet_variable_name] = new_value
					self.device_map[device][unocc_hsp_bacnet_variable_name] = new_value
					print("device %s, variable= %s, bacnet variable=%s, old value = %f, new value = %f" % (
					device, variable_name, occ_hsp_bacnet_variable_name, current_occ_heating_sp, new_value))
					print("device %s, variable= %s, bacnet variable=%s, old value = %f, new value = %f" % (
					device, variable_name, unocc_hsp_bacnet_variable_name, current_unocc_heating_sp, new_value))
					print()

			if variable_name == 'cooling_setpoint':
				occ_csp_bacnet_variable_name = self.point_map['occ_cooling_setpt']
				current_occ_cooling_sp = self.device_map[device][occ_csp_bacnet_variable_name].value

				unocc_csp_bacnet_variable_name = self.point_map['unocc_cooling_setpt']
				current_unocc_cooling_sp = self.device_map[device][unocc_csp_bacnet_variable_name].value

				if current_occ_cooling_sp != new_value or current_unocc_cooling_sp != new_value:
					self.device_map[device][occ_csp_bacnet_variable_name] = new_value
					self.device_map[device][unocc_csp_bacnet_variable_name] = new_value
					print("device %s, variable= %s, bacnet variable=%s, old value = %f, new value = %f" % (
					device, variable_name, occ_csp_bacnet_variable_name, current_occ_cooling_sp, new_value))
					print("device %s, variable= %s, bacnet variable=%s, old value = %f, new value = %f" % (
					device, variable_name, unocc_csp_bacnet_variable_name, current_unocc_cooling_sp, new_value))
					print()

	async def _read_and_publish(self, *args):

		for service_name in self.device_map:
			device = self.device_map[service_name]

			try:
				measurements = {}
				for point in self.point_map:
					bacnet_point_name = self.point_map[point]
					val = device[bacnet_point_name].value
					if type(val) == str:
						if val == "active":
							val = True
						else:
							val = False
					measurements[point] = val
				print(measurements)

				msg = xbos_pb2.XBOS(
					flexstat_state=flexstat_pb2.FlexstatState(
						time=int(time.time() * 1e9),
						space_temp_sensor=types.Double(value=measurements.get('space_temp_sensor', None)),
						minimum_proportional=types.Double(value=measurements.get('minimum_proportional', None)),
						active_cooling_setpt=types.Double(value=measurements.get('active_cooling_setpt', None)),
						active_heating_setpt=types.Double(value=measurements.get('active_heating_setpt', None)),
						unocc_cooling_setpt=types.Double(value=measurements.get('unocc_cooling_setpt', None)),
						unocc_heating_setpt=types.Double(value=measurements.get('unocc_heating_setpt', None)),
						occ_min_clg_setpt=types.Double(value=measurements.get('occ_min_clg_setpt', None)),
						occ_max_htg_setpt=types.Double(value=measurements.get('occ_max_htg_setpt', None)),
						override_timer=types.Double(value=measurements.get('override_timer', None)),
						occ_cooling_setpt=types.Double(value=measurements.get('occ_cooling_setpt', None)),
						occ_heating_setpt=types.Double(value=measurements.get('occ_heating_setpt', None)),
						current_mode_setpt=types.Double(value=measurements.get('current_mode_setpt', None)),
						ui_setpt=types.Double(value=measurements.get('ui_setpt', None)),
						cooling_need=types.Double(value=measurements.get('cooling_need', None)),
						heating_need=types.Double(value=measurements.get('heating_need', None)),
						unocc_min_clg_setpt=types.Double(value=measurements.get('unocc_min_clg_setpt', None)),
						unocc_max_htg_setpt=types.Double(value=measurements.get('unocc_max_htg_setpt', None)),
						min_setpt_diff=types.Double(value=measurements.get('min_setpt_diff', None)),
						min_setpt_limit=types.Double(value=measurements.get('min_setpt_limit', None)),
						space_temp=types.Double(value=measurements.get('space_temp', None)),
						cooling_prop=types.Double(value=measurements.get('cooling_prop', None)),
						heating_prop=types.Double(value=measurements.get('heating_prop', None)),
						cooling_intg=types.Double(value=measurements.get('cooling_intg', None)),
						heating_intg=types.Double(value=measurements.get('heating_intg', None)),
						fan=types.Int64(value=measurements.get('fan', None)),
						occupancy_mode=types.Int64(value=measurements.get('occupancy_mode', None)),
						setpt_override_mode=types.Int64(value=measurements.get('setpt_override_mode', None)),
						fan_alarm=types.Int64(value=measurements.get('fan_alarm', None)),
						fan_need=types.Int64(value=measurements.get('fan_need', None)),
						heating_cooling_mode=types.Int64(value=measurements.get('heating_cooling_mode', None)),
						occ_fan_auto_on=types.Int64(value=measurements.get('occ_fan_auto_on', None)),
						unocc_fan_auto_on=types.Int64(value=measurements.get('unocc_fan_auto_on', None)),
						fan_status=types.Int64(value=measurements.get('fan_status', None))
					)
				)
				await self.publish(self.namespace, service_name, False, msg)
				print("published at time_now = ", time_now)
			except:
				print("error for thermostat {0} !! continuing!".format(service_name))

parser = argparse.ArgumentParser()
parser.add_argument("config_file", help="config file ")
args = parser.parse_args()
config_file = args.config_file

with open(config_file) as f:
	driverConfig = yaml.safe_load(f)

xbosConfig = driverConfig['xbos']
waved = xbosConfig.get('waved', 'localhost:777')
wavemq = xbosConfig.get('wavemq', 'locahost:4516')
namespace = xbosConfig.get('namespace')
base_resource = xbosConfig.get('base_resource')
service_name_map = xbosConfig.get('service_name_map')
entity = xbosConfig.get('entity')
rate = xbosConfig.get('publish_rate', 60)
driver_id = xbosConfig.get('id', 'wattnode-driver')
check_setpoint_rate = xbosConfig.get('check_setpoint_rate', 30)
thermostat_config = driverConfig.get('thermostat_config')

xbos_cfg = {
	'waved': waved,
	'wavemq': wavemq,
	'namespace': namespace,
	'base_resource': base_resource,
	'entity': entity,
	'id': driver_id,
	'publish_rate': publish_rate,
	'check_setpoint_rate': check_setpoint_rate,
	'service_name_map': service_name_map,
	'config_file': config_file,
	'thermostat_config': thermostat_config
}

logging.basicConfig(level="INFO", format='%(asctime)s - %(name)s - %(message)s')
obj = FlexstatDriver(cfg=xbos_cfg)
run_loop()
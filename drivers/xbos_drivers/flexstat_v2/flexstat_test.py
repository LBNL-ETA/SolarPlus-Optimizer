import time
from pyxbos.process import XBOSProcess, b64decode, b64encode, schedule, run_loop
from pyxbos import xbos_pb2
from pyxbos import flexstat_pb2
from pyxbos import nullabletypes_pb2 as types
# from pyxbos.energise_pb2 import EnergiseMessage, LPBCStatus, LPBCCommand, SPBC, EnergiseError, EnergisePhasorTarget, ChannelStatus
# from pyxbos.c37_pb2 import Phasor, PhasorChannel
from datetime import datetime
from functools import partial
from collections import deque
import asyncio

class FlexstatDriver(XBOSProcess):

	def __init__(self, cfg):
		super().__init__(cfg)
		self.namespace = b64decode(cfg['namespace'])
		self.device_name = 'test_tstat'
		self._rate = cfg['rate']
		self._set_setpoint_rate = cfg.get("setpoint_rate", 1)
		self._default_time_threshold = cfg.get("default_time_threshold", 60)
		self._default_heating_setpoint = cfg.get("default_heating_setpoint", 67)
		self._default_cooling_setpoint = cfg.get("default_cooling_setpoint", 74)

		self.current_heating_sp = 20
		self.current_cooling_sp = 30

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
		self._setpoints = {}
		self._actuation_message_path = cfg.get("actuation_message_path", "flexstat_test/*/actuation")
		
		# Check message bus and extract latest setpoint list
		schedule(self._query_existing(path=self._actuation_message_path))

		# set subscription to any new action message that is published and extract setpoint list
		schedule(self.subscribe_extract(self.namespace, "flexstat_test/*/actuation", ".flexstatActuationMessage.setpoints", self._save_setpoints, "save_setpoints"))

		# read thermostat points every _rate seconds and publish
		schedule(self.call_periodic(self._rate, self._read_and_publish, runfirst=True))

		# periodically check if there is a need to change setpoints
		schedule(self.call_periodic(self._set_setpoint_rate, self._set_setpoints, runfirst=False))

	def extract_setpoint_dict(self, setpoint_values):
		setpoint_dict = {}
		for setpoint in setpoint_values:
			time = float(setpoint['changeTime'])/1e9
			setpoint_dict[time] = {}

			if 'heatingSetpoint' in setpoint.keys():
				setpoint_dict[time]['heating_setpoint'] = setpoint['heatingSetpoint'].get('value', None)

			if 'coolingSetpoint' in setpoint.keys():
				setpoint_dict[time]['cooling_setpoint'] = setpoint['coolingSetpoint'].get('value', None)
		return setpoint_dict

	async def _query_existing(self, path):
		responses = await self.query_topic(self.namespace, path, ".flexstatActuationMessage.setpoints")
		for response in responses:
			device = response.uri.split("/")[1]
			setpoint_dict = self.extract_setpoint_dict(setpoint_values=response.values[0])
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
				if self.current_heating_sp != new_value:
					print("device %s, variable= %s, old value = %f, new value = %f"%(device, variable_name,  self.current_heating_sp, new_value))
					self.current_heating_sp = new_value
			if variable_name == 'cooling_setpoint':
				if self.current_cooling_sp != new_value:
					print("device %s, variable= %s, old value = %f, new value = %f"%(device, variable_name,  self.current_cooling_sp, new_value))
					self.current_cooling_sp = new_value

			# TODO: uncomment this and change this
			# var_name_in_bacnet = self.point_map['variable_name']
			# current_value = self.device[var_name_in_bacnet].value

			# if current_value != new_value:
			# 	self.device[var_name_in_bacnet] = new_value

	async def _read_and_publish(self, *args):
		setpoint_list = []
		time_now = time.time()
		for i in range(5):
			change_time = time_now + i*20
			setpoint_list.append(
				flexstat_pb2.FlexstatSetpoints(
					change_time = int(change_time*1e9),
					heating_setpoint = types.Double(value = 20.2 + 10*i),
					cooling_setpoint = types.Double(value = 30.5 + 10*i),
				)
			)
		msg = xbos_pb2.XBOS(
				flexstat_actuation_message = flexstat_pb2.FlexstatActuationMessage(
					time = int(time_now*1e9),
					setpoints = setpoint_list
					)
				)
		await self.publish(self.namespace, "flexstat_test/test_tstat2/actuation", True, msg)
		print("published new setpoint list at time_now = ", time_now)

waved = 'localhost:777'
wavemq = 'localhost:4516'
namespace = 'GyA1TN-RJ1DWOjdBV-_2BZDKSH0qOZLeHCwz-Dmpqqy0EA=='
base_resource = 'flexstat_test'
entity = 'flexstat.ent'
driver_id = 'flexstat-test-driver'
rate = 2*60
setpoint_rate = 3
thermostat_config = {}

cfg = {
	'waved': waved,
	'wavemq': wavemq,
	'namespace': namespace,
	'base_resource': base_resource,
	'entity': entity,
	'id': driver_id,
	'thermostat_config': {},
	'rate': rate,
	'setpoint_rate': setpoint_rate
}
obj = FlexstatDriver(cfg)
run_loop()

import argparse
import yaml
import logging
import time
from pyxbos.process import XBOSProcess, b64decode, b64encode, schedule, run_loop
from pyxbos import xbos_pb2
from pyxbos import rtac_pb2
from pyxbos import nullabletypes_pb2 as types
from functools import partial
from collections import deque
import asyncio
import numpy as np
from pyfmi import load_fmu


class EmulatedBatteryDriver(XBOSProcess):
    def __init__(self, cfg):
        super().__init__(cfg)
        self.namespace = b64decode(cfg['namespace'])
        self.base_resource = cfg['base_resource']
        self._rate = cfg['publish_rate']
        self._set_setpoint_rate = cfg["check_setpoint_rate"]
        self.device_config = cfg['device_config']
        self.service_name = cfg['service_name']

        self._model_update_rate = self.device_config.get('model_update_rate', 30)
        self._inital_SOC = self.device_config.get('initial_SOC', 0)
        self._default_real_power_setpoint = self.device_config.get('default_real_power_setpoint', 0)
        self._min_real_power_setpoint = self.device_config.get('min_real_power_setpoint', -109000)
        self._max_real_power_setpoint = self.device_config.get('max_real_power_setpoint', 109000)

        self._default_time_threshold = self.device_config.get("time_threshold_revert_to_default", 14400)

        self._setpoints = {}
        self._actuation_message_path = ".rtacActuationMessage"
        self.device_control_flag = {}

        self.fmu_file = self.device_config.get('fmu_file')
        self.battery = load_fmu(self.fmu_file)
        self.battery.set('simple.SOC_0', self._inital_SOC)
        self.model_options = self.battery.simulate_options()
        self.model_options['initialize'] = True
        self.current_time = 0
        self.current_real_power_setpoint = self._default_real_power_setpoint

        # Check message bus and extract latest control flag and setpoint list
        actuation_message_uri = self.base_resource+"/"+self.service_name+"/actuation"
        schedule(self._query_existing(uri=actuation_message_uri))
        schedule(self._query_existing(uri=actuation_message_uri+"/control_flag"))
        #
        # # set subscription to any new action message that is published and extract setpoint list
        schedule(self.subscribe_extract(self.namespace, actuation_message_uri, self._actuation_message_path, self._save_setpoints, "save_setpoints"))
        schedule(self.subscribe_extract(self.namespace, actuation_message_uri+"/control_flag", self._actuation_message_path, self._save_setpoints, "save_setpoints"))

        # read controller points every _rate seconds and publish
        schedule(self.call_periodic(self._rate, self._read_and_publish, runfirst=True))
        schedule(self.call_periodic(self._model_update_rate, self._advance_time, runfirst=True))
        #
        # # periodically check if there is a need to change setpoints
        schedule(self.call_periodic(self._set_setpoint_rate, self._set_setpoints, runfirst=False))

    async def _advance_time(self):
        start = self.current_time
        end = self.current_time + self._model_update_rate

        power_setpoint = (['PSet'], np.array(
            [
                [start, self.current_real_power_setpoint],
                [end, self.current_real_power_setpoint]
            ]
        ))

        self.battery.simulate(start, end, power_setpoint, options=self.model_options)
        self.model_options['initialize'] = False
        self.current_time = self.current_time + self._model_update_rate

    def extract_setpoint_dict(self, setpoint_values):
        setpoint_dict = {}
        for setpoint in setpoint_values:
            time = float(setpoint['changeTime']) / 1e9
            setpoint_dict[time] = {}

            if 'realPowerSetpoint' in setpoint.keys():
                setpoint_dict[time]['realPowerSetpoint'] = setpoint['realPowerSetpoint'].get('realPowerSetpoint', None)

        return setpoint_dict

    async def _query_existing(self, uri):
        responses = await self.query_topic(self.namespace, uri, self._actuation_message_path)
        print("Extracting persisted messages")
        for response in responses:
            device = response.uri.split("/")[1]
            response_content =  response.values[0]
            control_flag = response_content.get('controlFlag', None)
            setpoints = response_content.get('setpoints', None)

            if control_flag != None:
                if not control_flag and self.device_control_flag.get(device, False):
                    self.change_setpoints(device=device, variable_name='realPowerSetpoint', new_value=self._default_real_power_setpoint)
                self.device_control_flag[device] = control_flag.get('value', False) == '1'

            if setpoints != None:
                setpoint_dict = self.extract_setpoint_dict(setpoint_values=setpoints)
                if not device in self._setpoints.keys():
                    self._setpoints[device] = setpoint_dict
                    print("no %s setpoints in setpoints_dict. extracting from persistent messsage"%device)

    def _save_setpoints(self, resp):
        print('inside subscribe_extract')
        device = resp.uri.split("/")[1]

        response_content = resp.values[0]
        control_flag = response_content.get('controlFlag', None)
        setpoints = response_content.get('setpoints', None)

        if control_flag != None:
            if not control_flag  and self.device_control_flag.get(device, False):
                self.change_setpoints(device=device, variable_name='realPowerSetpoint', new_value=self._default_real_power_setpoint)
            self.device_control_flag[device] = control_flag.get('value', False) == '1'

        if setpoints != None:
            setpoint_dict = self.extract_setpoint_dict(setpoint_values=setpoints)
            self._setpoints[device] = setpoint_dict

    async def _set_setpoints(self, *args):
        time_now = time.time()
        device_setpoint_dict = self._setpoints
        for device in device_setpoint_dict:
            control_flag = self.device_control_flag.get(device, False)
            real_power_setpoint = self._default_real_power_setpoint
            if control_flag:
                found = False
                setpoint_dict = device_setpoint_dict[device]
                first_change_time = sorted(setpoint_dict)[0]

                if abs(time_now - first_change_time) > self._default_time_threshold:
                    # CASE1: if the time_now is more than 4 hours before the 1st setpoint in the list of setpoints; set default setpoints
                    # CASE2: if the last time mpc published the setpoints (first change_time of setpoints is approximately the same time as the time MPC ran) is at least 4 hours before time_now, set defaults setpoints
                    real_power_setpoint = self._default_real_power_setpoint
                    # differential = self._default_differential_map[device]
                    print("CASE 1/2")
                elif time_now < first_change_time:
                    real_power_setpoint = setpoint_dict[first_change_time].get('real_power_setpoint', None)
                    print("first change time = = %s"%(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(first_change_time))))
                elif time_now >= first_change_time:
                    for change_time in sorted(setpoint_dict):
                        if not found and time_now < change_time:
                            found = True
                            # CASE3: if time_now is between the list of setpoints, get the new setpoints
                            real_power_setpoint = setpoint_dict[change_time].get('real_power_setpoint', None)
                            print("CASE 3: change_time = = %s"%(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(change_time))))

                    if not found:
                        last_change_time = sorted(setpoint_dict, reverse=True)[0]
                        if (time_now - last_change_time) > self._default_time_threshold:
                            # CASE4: time now is at least 4 hours ahead of the last time MPC published the setpoints, set to default setpoints
                            real_power_setpoint= self._default_real_power_setpoint
                            # differential = self._default_differential_map[device]
                            print("CASE 4")
                        else:
                            # CASE5: time_now is less that 4 hours ahead of the last setpoint forecase, do nothing
                            real_power_setpoint = None
                            print("CASE 5")

                self.change_setpoints(device=device, variable_name='real_power_setpoint', new_value=real_power_setpoint)

    def change_setpoints(self, device, variable_name, new_value):
        if new_value != None:
            new_value = round(new_value, 2)
            if variable_name == 'real_power_setpoint':
                if self._max_real_power_setpoint[device] < new_value:
                    print("new setpoint = %f more than max limit=%f for %s. changing new setpoint to max setpoint limit" % (
                        new_value, self._max_real_power_setpoint, device))
                    new_value = self._max_real_power_setpoint

                if self._min_real_power_setpoint > new_value:
                    print("new setpoint = %f less than min limit=%f for %s. changing new setpoint to min setpoint limit" % (
                        new_value, self._min_real_power_setpoint, device))
                    new_value = self._min_real_power_setpoint

                register_name = 'real_power_setpoint'
                unit = self.unit_id
                current_value = self.current_real_power_setpoint

                if current_value != new_value:
                    value_to_be_written = new_value
                    try:
                        print("writting to %s, value=%f, unit=%d" % (register_name, value_to_be_written, unit))
                        self.current_real_power_setpoint = value_to_be_written
                    except Exception as e:
                        print("exception happened when writing %f to setpoint for %s, %r" % (
                        value_to_be_written, device, e))

                    print("device %s, variable= %s, modbus variable=%s, old value = %f, new value = %f, value written=%f" % (
                        device, variable_name, register_name, current_value, new_value, value_to_be_written))
                else:
                    print("no change in setpoint, not changing")

    async def _read_and_publish(self, *args):

        try:
            measurements = {'real_power_setpoint': self.battery.get('PSet'), 'battery_soc': self.battery.get('SOC_meas')}

            time_now = time.time() * 1e9

            msg = xbos_pb2.XBOS(
                rtac_state=rtac_pb2.RtacState(
                    time=int(time_now),
                    real_power_setpoint = types.Double(value=measurements.get('real_power_setpoint', None)),
                    battery_soc = types.Double(value=measurements.get('battery_soc', None))
                )
            )
            resource = self.base_resource + "/" + self.service_name
            await self.publish(self.namespace, resource, False, msg)
            print("published at time_now = %s on topic %s" % (
            time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time_now / 1e9)), resource))
        except Exception as e:
            print("error occured in service_name = %s! reconnecting and continuing, error = %r" % (self.service_name, e))

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
service_name = xbosConfig.get('service_name')
entity = xbosConfig.get('entity')
rate = xbosConfig.get('publish_rate', 60)
driver_id = xbosConfig.get('id', 'battery-emulator-driver')
check_setpoint_rate = xbosConfig.get('check_setpoint_rate', 30)
device_config = driverConfig.get('device_config')

xbos_cfg = {
    'waved': waved,
    'wavemq': wavemq,
    'namespace': namespace,
    'base_resource': base_resource,
    'entity': entity,
    'id': driver_id,
    'publish_rate': rate,
    'check_setpoint_rate': check_setpoint_rate,
    'service_name': service_name,
    'config_file': config_file,
    'device_config': device_config
}

logging.basicConfig(level="INFO", format='%(asctime)s - %(name)s - %(message)s')
obj = EmulatedBatteryDriver(cfg=xbos_cfg)
run_loop()

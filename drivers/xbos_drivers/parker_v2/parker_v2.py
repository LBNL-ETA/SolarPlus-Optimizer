import argparse
import yaml
import logging
import time
from pyxbos.modbus_driver import Modbus_Driver
from pyxbos.process import XBOSProcess, b64decode, b64encode, schedule, run_loop
from pyxbos import xbos_pb2
from pyxbos import parker_pb2
from pyxbos import nullabletypes_pb2 as types
from functools import partial
from collections import deque
import asyncio


class ParkerDriver(XBOSProcess):
    def __init__(self, cfg):
        super().__init__(cfg)
        self.namespace = b64decode(cfg['namespace'])
        self.base_resource = cfg['base_resource']
        self._rate = cfg['publish_rate']
        self._set_setpoint_rate = cfg["check_setpoint_rate"]
        self.service_name_map = cfg['service_name_map']
        self.modbus_config = cfg['modbus_config']

        config_file = cfg['config_file']

        self.modbus_device = Modbus_Driver(config_file=config_file, config_section='modbus')
        self.modbus_device.initialize_modbus()

        self._default_time_threshold = self.modbus_config.get("time_threshold_revert_to_default", 14400)

        self._default_setpoint_map = self.modbus_config.get("default_setpoint_map", {'refrigerator': 33, 'freezer': -7})
        self._max_setpoint_limit_map = self.modbus_config.get("max_setpoint_limit_map", {'refrigerator': 38, 'freezer': -2})
        self._min_setpoint_limit_map = self.modbus_config.get("min_setpoint_limit_map", {'refrigerator': 34, 'freezer': -30})

        #self._default_differential_map = self.modbus_config.get("default_differential_map", {'refrigerator': **, 'freezer': **})
        #self._differential_limit_map = self.modbus_config.get("differential_limit_map", {'refrigerator': **, 'freezer': **})

        self._setpoints = {}
        self._actuation_message_path = ".parkerActuationMessage"
        self.device_control_flag = {}

        # Check message bus and extract latest control flag and setpoint list
        for device_name in self.service_name_map:
            actuation_message_uri = self.base_resource+"/"+device_name+"/actuation"
            schedule(self._query_existing(uri=actuation_message_uri))
            schedule(self._query_existing(uri=actuation_message_uri+"/control_flag"))

            # set subscription to any new action message that is published and extract setpoint list
            schedule(
                self.subscribe_extract(self.namespace, actuation_message_uri, self._actuation_message_path,
                                    self._save_setpoints, "save_setpoints"))
            schedule(
                self.subscribe_extract(self.namespace, actuation_message_uri+"/control_flag", self._actuation_message_path,
                                    self._save_setpoints, "save_setpoints"))

        # read controller points every _rate seconds and publish
        schedule(self.call_periodic(self._rate, self._read_and_publish, runfirst=True))

        # periodically check if there is a need to change setpoints
        schedule(self.call_periodic(self._set_setpoint_rate, self._set_setpoints, runfirst=False))

    def extract_setpoint_dict(self, setpoint_values):
        setpoint_dict = {}
        for setpoint in setpoint_values:
            time = float(setpoint['changeTime']) / 1e9
            setpoint_dict[time] = {}

            if 'setpoint' in setpoint.keys():
                setpoint_dict[time]['setpoint'] = setpoint['setpoint'].get('value', None)

            if 'differential' in setpoint.keys():
                setpoint_dict[time]['differential'] = setpoint['differential'].get('value', None)
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
                    self.change_setpoints(device=device, variable_name='setpoint', new_value=self._default_setpoint_map[device])
                    # self.change_setpoints(device=device, variable_name='differential', new_value=self._default_differential_map[device])

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
                self.change_setpoints(device=device, variable_name='setpoint', new_value=self._default_setpoint_map[device])
                # self.change_setpoints(device=device, variable_name='differential', new_value=self._default_differential_map[device])
            self.device_control_flag[device] = control_flag.get('value', False) == '1'

        if setpoints != None:
            setpoint_dict = self.extract_setpoint_dict(setpoint_values=setpoints)
            self._setpoints[device] = setpoint_dict

    async def _set_setpoints(self, *args):
        time_now = time.time()
        device_setpoint_dict = self._setpoints
        for device in device_setpoint_dict:
            control_flag = self.device_control_flag.get(device, False)
            if control_flag:
                found = False
                setpoint_dict = device_setpoint_dict[device]
                first_change_time = sorted(setpoint_dict)[0]

                if abs(time_now - first_change_time) > self._default_time_threshold:
                    # CASE1: if the time_now is more than 4 hours before the 1st setpoint in the list of setpoints; set default setpoints
                    # CASE2: if the last time mpc published the setpoints (first change_time of setpoints is approximately the same time as the time MPC ran) is at least 4 hours before time_now, set defaults setpoints
                    setpoint = self._default_setpoint_map[device]
                    # differential = self._default_differential_map[device]
                    print("CASE 1/2")
                elif time_now < first_change_time:
                    setpoint = setpoint_dict[first_change_time].get('setpoint', None)
                    differential = setpoint_dict[first_change_time].get('differential', None)
                    print("first change time = = %s"%(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(first_change_time))))
                elif time_now >= first_change_time:
                    for change_time in sorted(setpoint_dict):
                        if not found and time_now < change_time:
                            found = True
                            # CASE3: if time_now is between the list of setpoints, get the new setpoints
                            setpoint = setpoint_dict[change_time].get('setpoint', None)
                            differential = setpoint_dict[change_time].get('differential', None)
                            print("CASE 3: change_time = = %s"%(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(change_time))))

                    if not found:
                        last_change_time = sorted(setpoint_dict, reverse=True)[0]
                        if (time_now - last_change_time) > self._default_time_threshold:
                            # CASE4: time now is at least 4 hours ahead of the last time MPC published the setpoints, set to default setpoints
                            setpoint = self._default_setpoint_map[device]
                            # differential = self._default_differential_map[device]
                            print("CASE 4")
                        else:
                            # CASE5: time_now is less that 4 hours ahead of the last setpoint forecase, do nothing
                            setpoint = None
                            differential = None
                            print("CASE 5")

                self.change_setpoints(device=device, variable_name='setpoint', new_value=setpoint)
                self.change_setpoints(device=device, variable_name='differential', new_value=differential)
            else:
                print("control flag for device %s is False. Not changing setpoints"%(device))


    def change_setpoints(self, device, variable_name, new_value):
        if new_value != None:
            new_value = round(new_value, 1)
            if variable_name == 'setpoint':

                if self._max_setpoint_limit_map[device] < new_value:
                    print("new setpoint = %f more than max limit=%f for %s. changing new setpoint to max setpoint limit"%(new_value, self._max_setpoint_limit_map[device], device))
                    new_value = self._max_setpoint_limit_map[device]

                if self._min_setpoint_limit_map[device] > new_value:
                    print("new setpoint = %f less than min limit=%f for %s. changing new setpoint to min setpoint limit" % (new_value, self._min_setpoint_limit_map[device], device))
                    new_value = self._min_setpoint_limit_map[device]

                register_name = 'setpoint'
                unit = self.service_name_map[device]
                current_value = round(self.modbus_device.read_holding_register(register_name=register_name, unit=unit)/10, 1)

                if current_value != new_value:
                    value_to_be_written = int(new_value*10)
                    try:
                        ## adding a synchronous sleep
                        time.sleep(5)
                        print("writting to %s, value=%d, unit=%d"%(register_name, value_to_be_written, unit))
                        self.modbus_device.write_register(register_name=register_name, value=value_to_be_written, unit=unit)
                    except Exception as e:
                        print("exception happened when writing %d to setpoint for %s, %r"%(value_to_be_written, device, e))

                    print("device %s, variable= %s, modbus variable=%s, old value = %f, new value = %f, value written=%d" % (device, variable_name, register_name, current_value, new_value, value_to_be_written))
                else:
                    print("no change in setpoint, not changing")

            if variable_name == 'differential':
                print("not changing differential at this point")

                # if self._differential_limit_map[device] > new_value:
                #     new_value = self._differential_limit_map[device]
                #
                # register_name = 'r0'
                # unit = self.service_name_map[device]
                # current_value = round(self.modbus_device.read_holding_register(register_name=register_name, unit=unit)/10, 2)
                #
                # if current_value != new_value:
                #     self.modbus_device.write_register(register_name=register_name, value=new_value, unit=unit)
                #
                #     print("device %s, variable= %s, modbus variable=%s, old value = %f, new value = %f" % (device, variable_name, register_name, current_value, new_value))
                # else:
                #     print("no change in setpoint, not changing")

    async def _read_and_publish(self, *args):

        for service_name in self.service_name_map:
            unit_id = self.service_name_map[service_name]

            try:
                output = self.modbus_device.get_data(unit=unit_id)


                # This is necessary because we need to bitwise operations to unpack the
                # the flags received from the modbus register
                regulator_flag_1 = output['regulator_flag_1']
                output['energy_saving_regulator_flag'] = bool(regulator_flag_1 & 0x0100)
                output['energy_saving_real_time_regulator_flag'] = bool(regulator_flag_1 & 0x0200)
                output['service_request_regulator_flag'] = bool(regulator_flag_1 & 0x0400)

                regulator_flag_2 = output['regulator_flag_2']
                output['on_standby_regulator_flag'] = bool(regulator_flag_2 & 0x0001)
                output['new_alarm_to_read_regulator_flag'] = bool(regulator_flag_2 & 0x0080)
                output['defrost_status_regulator_flag']	= bool(regulator_flag_2 & 0x0700)

                digital_io_status = output['digital_io_status']
                output['door_switch_input_status'] = bool(digital_io_status & 0x0001)
                output['multipurpose_input_status'] = bool(digital_io_status & 0x0002)
                output['compressor_status'] = bool(digital_io_status & 0x0100)
                output['output_defrost_status'] = bool(digital_io_status & 0x0200)
                output['fans_status'] = bool(digital_io_status & 0x0400)
                output['output_k4_status'] = bool(digital_io_status & 0x0800)

                digital_output_flags = output['digital_output_flags']
                output['energy_saving_status'] = bool(digital_output_flags & 0x0100)
                output['service_request_status'] =	bool(digital_output_flags & 0x0200)
                output['resistors_activated_by_aux_key_status'] = bool(digital_output_flags & 0x001)
                output['evaporator_valve_state'] = bool(digital_output_flags & 0x002)
                output['output_defrost_state'] = bool(digital_output_flags & 0x004)
                output['output_lux_state'] =	bool(digital_output_flags & 0x008)
                output['output_aux_state'] =	bool(digital_output_flags & 0x0010)
                output['resistors_state'] = bool(digital_output_flags & 0x0020)
                output['output_alarm_state'] =	bool(digital_output_flags & 0x0040)
                output['second_compressor_state'] =	bool(digital_output_flags & 0x0080)

                alarm_status = output['alarm_status']
                #print(format(output['alarm_status'], '#010b'))
                output['probe1_failure_alarm'] = bool(alarm_status & 0x0100)
                output['probe2_failure_alarm'] = bool(alarm_status & 0x0200)
                output['probe3_failure_alarm'] = bool(alarm_status & 0x0400)
                output['minimum_temperature_alarm'] = bool(alarm_status & 0x1000)
                output['maximum_temperture_alarm'] = bool(alarm_status & 0x2000)
                output['condensor_temperature_failure_alarm'] = bool(alarm_status & 0x4000)
                output['condensor_pre_alarm'] = bool(alarm_status & 0x8000)
                output['door_alarm'] = bool(alarm_status & 0x0004)
                output['multipurpose_input_alarm'] = bool(alarm_status & 0x0008)
                output['compressor_blocked_alarm'] = bool(alarm_status & 0x0010)
                output['power_failure_alarm'] = bool(alarm_status & 0x0020)
                output['rtc_error_alarm'] = bool(alarm_status & 0x0080)
                #print(output['rtc_error_alarm'])
                #print(format(output['rtc_error_alarm'], '#010b'))
                # print(output)

                next_defrost_counter = output.get('next_defrost_counter', None)
                if next_defrost_counter != None:
                    next_defrost_counter*=15

                time_until_defrost = output.get('time_until_defrost', None)
                if time_until_defrost != None:
                    time_until_defrost*=15

                list_of_double_values = ['cabinet_temperature', 'evaporator_temperature', 'auxiliary_temperature', 'C6', 'C7', 'd2', 'd9',
                                         'active_setpoint', 'setpoint', 'r1', 'r2', 'A1', 'A4', 'F1']

                for variable in list_of_double_values:
                    value = output.get(variable, None)
                    if value != None:
                        output[variable]/=10

                # set these for setting defrost times
                #for variable in ['Hd1', 'Hd2', 'Hd3', 'Hd4', 'Hd5', 'Hd6']:

                time_now = time.time() * 1e9

                msg = xbos_pb2.XBOS(
                    parker_state = parker_pb2.ParkerState(
                        time = int(time_now),
                        compressor_working_hours=types.Double(value=output.get('compressor_working_hours', None)),
                        on_standby_status=types.Int64(value=output.get('on_standby_status', None)),
                        light_status=types.Int64(value=output.get('light_status', None)),
                        aux_output_status=types.Int64(value=output.get('aux_output_status', None)),
                        next_defrost_counter=types.Double(value=output.get('next_defrost_counter', None)),

                        door_switch_input_status=types.Int64(value=output.get('door_switch_input_status', None)),
                        multipurpose_input_status=types.Int64(value=output.get('multipurpose_input_status', None)),
                        compressor_status=types.Int64(value=output.get('compressor_status', None)),
                        output_defrost_status=types.Int64(value=output.get('output_defrost_status', None)),
                        fans_status=types.Int64(value=output.get('fans_status', None)),
                        output_k4_status=types.Int64(value=output.get('output_k4_status', None)),

                        cabinet_temperature=types.Double(value=output.get('cabinet_temperature', None)),
                        evaporator_temperature=types.Double(value=output.get('evaporator_temperature', None)),
                        auxiliary_temperature=types.Double(value=output.get('auxiliary_temperature', None)),

                        probe1_failure_alarm=types.Int64(value=output.get('probe1_failure_alarm', None)),
                        probe2_failure_alarm=types.Int64(value=output.get('probe2_failure_alarm', None)),
                        probe3_failure_alarm=types.Int64(value=output.get('probe3_failure_alarm', None)),
                        minimum_temperature_alarm=types.Int64(value=output.get('minimum_temperature_alarm', None)),
                        maximum_temperture_alarm=types.Int64(value=output.get('maximum_temperture_alarm', None)),
                        condensor_temperature_failure_alarm=types.Int64(value=output.get('condensor_temperature_failure_alarm', None)),
                        condensor_pre_alarm=types.Int64(value=output.get('condensor_pre_alarm', None)),
                        door_alarm=types.Int64(value=output.get('door_alarm', None)),
                        multipurpose_input_alarm=types.Int64(value=output.get('multipurpose_input_alarm', None)),
                        compressor_blocked_alarm=types.Int64(value=output.get('compressor_blocked_alarm', None)),
                        power_failure_alarm=types.Int64(value=output.get('power_failure_alarm', None)),
                        rtc_error_alarm=types.Int64(value=output.get('rtc_error_alarm', None)),

                        energy_saving_regulator_flag=types.Int64(value=output.get('energy_saving_regulator_flag', None)),
                        energy_saving_real_time_regulator_flag=types.Int64(value=output.get('energy_saving_real_time_regulator_flag', None)),
                        service_request_regulator_flag=types.Int64(value=output.get('service_request_regulator_flag', None)),
                        on_standby_regulator_flag=types.Int64(value=output.get('on_standby_regulator_flag', None)),
                        new_alarm_to_read_regulator_flag=types.Int64(value=output.get('new_alarm_to_read_regulator_flag', None)),
                        defrost_status_regulator_flag=types.Int64(value=output.get('defrost_status_regulator_flag', None)),
                        active_setpoint=types.Double(value=output.get('active_setpoint', None)),
                        time_until_defrost=types.Double(value=output.get('time_until_defrost', None)),
                        current_defrost_counter=types.Int64(value=output.get('current_defrost_counter', None)),
                        compressor_delay=types.Int64(value=output.get('compressor_delay', None)),
                        num_alarms_in_history=types.Int64(value=output.get('num_alarms_in_history', None)),

                        energy_saving_status=types.Int64(value=output.get('energy_saving_status', None)),
                        service_request_status=types.Int64(value=output.get('service_request_status', None)),
                        resistors_activated_by_aux_key_status=types.Int64(value=output.get('resistors_activated_by_aux_key_status', None)),
                        evaporator_valve_state=types.Int64(value=output.get('evaporator_valve_state', None)),
                        output_defrost_state=types.Int64(value=output.get('output_defrost_state', None)),
                        output_lux_state=types.Int64(value=output.get('output_lux_state', None)),
                        output_aux_state=types.Int64(value=output.get('output_aux_state', None)),
                        resistors_state=types.Int64(value=output.get('resistors_state', None)),
                        output_alarm_state=types.Int64(value=output.get('output_alarm_state', None)),
                        second_compressor_state=types.Int64(value=output.get('second_compressor_state', None)),

                        setpoint=types.Double(value=output.get('setpoint', None)),

                        r1=types.Double(value=output.get('r1', None)),
                        r2=types.Double(value=output.get('r2', None)),
                        r4=types.Double(value=output.get('r4', None)),

                        C0=types.Double(value=output.get('C0', None)),
                        C1=types.Double(value=output.get('C1', None)),

                        d0=types.Double(value=output.get('d0', None)),
                        d3=types.Double(value=output.get('d3', None)),
                        d5=types.Double(value=output.get('d5', None)),
                        d7=types.Double(value=output.get('d7', None)),
                        d8=types.Int64(value=output.get('d8', None)),

                        A0=types.Int64(value=output.get('A0', None)),
                        A1=types.Double(value=output.get('A1', None)),
                        A2=types.Int64(value=output.get('A2', None)),
                        A3=types.Int64(value=output.get('A3', None)),
                        A4=types.Double(value=output.get('A4', None)),
                        A5=types.Int64(value=output.get('A5', None)),
                        A6=types.Double(value=output.get('A6', None)),
                        A7=types.Double(value=output.get('A7', None)),
                        A8=types.Double(value=output.get('A8', None)),
                        A9=types.Double(value=output.get('A9', None)),

                        F0=types.Int64(value=output.get('F0', None)),
                        F1=types.Double(value=output.get('F1', None)),
                        F2=types.Int64(value=output.get('F2', None)),
                        F3=types.Double(value=output.get('F3', None)),

                        # clear_compressor_working_hours=types.Int64(value=output.get('clear_compressor_working_hours', None)),
                        # buzzer_control=types.Int64(value=output.get('buzzer_control', None)),
                        # defrost_control=types.Int64(value=output.get('defrost_control', None)),
                        # start_resistors=types.Int64(value=output.get('start_resistors', None)),
                        P2=types.Int64(value=output.get('P2', None)),
                        P3=types.Int64(value=output.get('P3', None)),
                        r0=types.Double(value=output.get('r0', None)),
                        r3=types.Int64(value=output.get('r3', None)),
                        C2=types.Double(value=output.get('C2', None)),
                        C3=types.Double(value=output.get('C3', None)),
                        C4=types.Double(value=output.get('C4', None)),
                        C5=types.Double(value=output.get('C5', None)),
                        C6=types.Double(value=output.get('C6', None)),
                        C7=types.Double(value=output.get('C7', None)),
                        C8=types.Double(value=output.get('C8', None)),
                        C9=types.Double(value=output.get('C9', None)),
                        d1=types.Int64(value=output.get('d1', None)),
                        d2=types.Double(value=output.get('d2', None)),
                        d4=types.Int64(value=output.get('d4', None)),
                        d9=types.Double(value=output.get('d9', None)),
                        da=types.Double(value=output.get('da', None)),
                    )
                )
                resource = self.base_resource + "/" + service_name
                await self.publish(self.namespace, resource, False, msg)
                print("published at time_now = %s on topic %s" % (time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time_now / 1e9)), resource))
            except Exception as e:
                print("error occured in service_name = %s! reconnecting and continuing, error = %r"%(service_name, e))
                self.modbus_device.reconnect()

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
driver_id = xbosConfig.get('id', 'parker-driver')
check_setpoint_rate = xbosConfig.get('check_setpoint_rate', 30)
modbus_config = driverConfig.get('modbus')

xbos_cfg = {
    'waved': waved,
    'wavemq': wavemq,
    'namespace': namespace,
    'base_resource': base_resource,
    'entity': entity,
    'id': driver_id,
    'publish_rate': rate,
    'check_setpoint_rate': check_setpoint_rate,
    'service_name_map': service_name_map,
    'config_file': config_file,
    'modbus_config': modbus_config
}

logging.basicConfig(level="INFO", format='%(asctime)s - %(name)s - %(message)s')
obj = ParkerDriver(cfg=xbos_cfg)
run_loop()

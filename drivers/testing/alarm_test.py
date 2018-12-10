# python3 alarm_test.py fridge_config.yaml alarm_output.json

import os,sys
import time
from struct import *
import signal
import json
import argparse
# Add ../modbus_folder to path for Modbus_Driver
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
modbus_folder='modbus_driver'
sys.path.append(os.path.join(parent_dir, modbus_folder))
from modbus_driver import Modbus_Driver
from pymodbus.constants import Endian
from pymodbus.payload import BinaryPayloadDecoder

def read_HACCP(obj,num_alarms):
    HACCP_dict = {}
    base_address = 501
    alarm_num = 0
    while (num_alarms > 0):
        reg_num = 0
        HACCP_name = "HACCP_" + str(alarm_num)

        HACCP_reg = HACCP_name + str(reg_num)
        HACCP_dict[HACCP_reg] = obj.decode_register(base_address,"16uint")

        HACCP_reg = HACCP_name + str(reg_num+1)
        HACCP_dict[HACCP_reg] = obj.decode_register(base_address+1,"16uint")

        HACCP_reg = HACCP_name + str(reg_num+2)
        HACCP_dict[HACCP_reg] = obj.decode_register(base_address+2,"16uint")

        HACCP_reg = HACCP_name + str(reg_num+3)
        HACCP_dict[HACCP_reg] = obj.decode_register(base_address+3,"16uint")

        base_address += 4
        num_alarms -= 1

    return HACCP_dict

def and_true(alarm_status,mask):
    # Mask alarm status and check if it is the same as mask to return True/False
    if ((alarm_status & mask) == mask):
        return True
    else:
        return False


def decode_alarm(alarm_status):
    # Decode alarm status and put into dictionary with boolean values

    alarm_dict = {}
    alarm_dict['probe1_failure_alarm'] = and_true(alarm_status,0x0100)
    alarm_dict['probe2_failure_alarm'] = and_true(alarm_status,0x0200)
    alarm_dict['probe3_failure_alarm']	= and_true(alarm_status,0x0400)
    alarm_dict['minimum_temperature_alarm']	= and_true(alarm_status,0x1000)
    alarm_dict['maximum_temperture_alarm'] = and_true(alarm_status,0x2000)
    alarm_dict['condensor_temperature_failure_alarm'] = and_true(alarm_status,0x4000)
    alarm_dict['condensor_pre_alarm'] = and_true(alarm_status,0x8000)
    alarm_dict['door_alarm'] = and_true(alarm_status,0x0004)
    alarm_dict['multipurpose_input_alarm'] = and_true(alarm_status,0x0008)
    alarm_dict['compressor_blocked_alarm'] = and_true(alarm_status,0x0010)
    alarm_dict['power_failure_alarm'] = and_true(alarm_status,0x0020)
    alarm_dict['rtc_error_alarm'] = and_true(alarm_status,0x0080)
    return alarm_dict

def set_check(modbus_object,register,set_value):
    modbus_object.write_register(register, set_value)
    assert(modbus_object.read_register(register)==set_value)
    print(register + " was set correctly")

def set_params(obj):

    # Need to decode the alarms using pack/unpack not sure of the format differentiating
    # AL, AH, ld, PF
    # Since my screen does not work on my device I cannot differentiate codes on screen

    # 3. Clear the HAACP alarms, I was having problems with this on my device
    # These registers are write only so they cannot be in the register dictionary
    #obj.write_data(0x465, 1) # clear_HACCP_historian
    #obj.write_data(0x490, 1) # clear_HACCP_new_alarm_flag


    # 4. Set parameters related to refrigerator control

    # working setpoint differential
    set_check(obj,'r0',5)

    # minimum working setpoint
    set_check(obj,'r1',-50)

    # maximum working setpoint
    set_check(obj,'r2',50)

    # Measured input for low temperature alarm
    # Set 0 for cabinet probe, and 1 for evaporation probe, 2 for auxillary probe
    set_check(obj,'A0',0)

    # Measured input for high temperature alarm
    # Set 0 for cabinet probe and 1 for auxillary probe
    set_check(obj,'A3',0)

    # Temperature for low temperature alarm to activate values from -99 to 99 C/F
    set_check(obj,'A1',-10) # Default is -10

    # Temperature for high temperature alarm to activate values from -99 to 99 C/F
    set_check(obj,'A4',5) # Default is 10

    # Temperature for high temperature alarm to activate values from -99 to 99 C/F
    set_check(obj,'A5',1) # Default is 10

    # Delay for AH after turning on controller, values are from 0-240 minutes
    set_check(obj,'A6',2) # Default is 120

    # Temperature alarm delay, values are from 0-240 minutes
    set_check(obj,'A7',2) # Default is 15

    # High temperature alarm delay after the end of the defrost
    # (only if A3 = 0 or if P4 = 1 and A3 = 1)
    set_check(obj,'A8',2) # Default is 15

    # High temperature alarm delay after the deactivation of the microport input
    # (only if A3 = 0 or if P4 = 1 and A3 = 1)
    set_check(obj,'A9',15) # Default is 15

    # Delay recording of power failure alarm
    # This one is not related to temperature: AA: delay recording of power failure alarm
    set_check(obj,'AA',5) # Default is 1



    # Defrost Parameters

    # The behavior of the defrost is dependent on parameters d0-dA.
    # The key parameter to look at to understand the operation is d8.
    # There are four defrost methods for when the defrost will activate:
    # controller on time, compressor run time, evaporator temperature below a
    # certain temperature for so long, or at specified times. Once the defrost
    # is triggered, it will last for a specified duration (d3).
    # After this duration there is a drip delay (d7) during which the defrost
    # operation and normal operation are suspended.
    # The refrigerator evaporators at BLR are air defrost so the defrost
    # output will be hooked up to the fans. The freezer evaporator is electric
    # resistance defrost so the defrost output will be hooked up to the defrost heater.

    # Kind of defrost interval
    # 0 = PERIODIC - the defrost will be activated when the
    #     controller has remained turned on for time d0
    # 1 = PERIODIC - the defrost will be activated when the
    #     compressor has remained turned on for time d0
    # 2 = PERIODIC - the defrost will be activated when the
    #     evaporator temperature has remained below temperature d9 for time d0
    # 3 = REAL TIME - defrosting will be activated at the times established
    #     by parameters Hd1 ... Hd6
    set_check(obj,'d8',0) # Default is 0

    # defrost duration if P3 = 0 or 2;
    # maximum defrost duration if P3 = 1
    # 0 = the defrost will never be activated
    set_check(obj,'d3',30) # Default is 30 (minutes)

     # drip delay
    set_check(obj,'d7',2) # Default is 2 (minutes)


    # Setpoint
    set_check(obj,'SP',0) #  r1 <= SP <= r2, default is zero

    set_check(obj,'p4',0) # Default is 1
    set_check(obj,'p3',0) # Default is:
    set_check(obj,'F0',2) # Default is:
    set_check(obj,'F2',2) # Default is:
    set_check(obj,'i0',0) # Default is:
    set_check(obj,'i5',0) # Default is:

def cleanup(filename):
    outfile = open(filename, "a")
    outfile.write("]")
    outfile.close()
    print("Closing file and saving results")




#signal.signal(signal.SIGINT, signal_handler)
def main(config,output_file):
    obj = Modbus_Driver(config)
    obj.initialize_modbus()
    set_params(obj)
    output = {}
    count = 0
    filename = output_file
    with open(filename, 'w') as outfile:
        outfile.write('[')
        while(1):
            print("Recording data")
            output = obj.get_data()
            output['time'] = int(time.time())
            output['decoded_alarm'] = decode_alarm(output['alarm_status'])
            if (output['num_alarms_in_history'] > 0):
                output['HACCP'] = read_HACCP(obj,output['num_alarms_in_history'])
            json.dump(output, outfile)
            print("Going to sleep")
            print("If you want to stop test press ctrl+c now...")
            time.sleep(15)
            outfile.write(',')
            count += 1
    obj.kill_modbus()


global filename
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("config", help="config file")
    parser.add_argument("output_file", help="config file")

    args = parser.parse_args()
    config_file = args.config
    filename = args.output_file
    try:
        main(config_file,filename)
    except KeyboardInterrupt:
        cleanup(filename)

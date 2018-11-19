from modbus_driver import Modbus_Driver
import time
from struct import *

from pymodbus.constants import Endian
from pymodbus.payload import BinaryPayloadDecoder

def set_default(register_dict,obj):
    """
    register_dict ---  Dictionary of registers which contains:
        {register_name: [register_type, register_address, default_value, new_value]}
    obj --- Modbus_Driver object
    This function sets all registers contained in the dictionary passed in to the
    new_value specified in the list
    """
    for key in register_dict:
        obj.write_register(key,register_dict[key][2])

def set_all_param(register_dict,obj):
    """
    register_dict ---  Dictionary of registers which contains:
        {register_name: [register_type, register_address, default_value, new_value]}
    obj --- Modbus_Driver object
    This function sets all registers contained in the dictionary passed in to the
    new_value specified in the list
    After the parameter has been changed from the new_value specified it is changed
    back to its original value. This is to minimize the interaction between all of
    the parameters of the device while testing.
    """
    for key in register_dict:
        pre_write = obj.decode_register(register_dict[key][0],'16int')
        obj.write_register(key,register_dict[key][3])
        post_write = obj.decode_register(register_dict[key][0],'16int')
        obj.write_register(key,pre_write)
        final_write = obj.decode_register(register_dict[key][0],'16int')
        print("For parameter " + key + " default: " +str(pre_write) + " test parameter: " + str(post_write) + " reset value: " + str(final_write))

obj = Modbus_Driver("fridge_config.yaml")
obj.initialize_modbus()

output = obj.get_data()
print(output)

print("----SETTING SP to 20-----")
obj.write_register('SP', 20)

print()
print("Register values after changing SP value:")
output = obj.get_data()
print(output)

#set_default(obj.holding_register_dict,obj)
#set_all_param(obj.holding_register_dict,obj)
"""
print("               ")
print("               ")
print("               ")
print("               ")

output = obj.get_data()
print(output)
"""


obj.kill_modbus()

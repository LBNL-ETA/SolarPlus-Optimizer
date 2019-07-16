from modbus_driver import Modbus_Driver
import time
from struct import *

from pymodbus.constants import Endian
from pymodbus.payload import BinaryPayloadDecoder




obj = Modbus_Driver("bat_driver.yaml",)


obj.initialize_modbus()
print("current values of the registers")
output = obj.get_data()
print(output)

print("------Setting real power setpoint to 100-------")
obj.write_register('real_power_setpoint', 100)
print("------Setting active power output limit to 120-------")
obj.write_register('active_power_output_limit', 120)

output = obj.get_data()
print()
print("new values of the registers")
output = obj.get_data()
print(output)


obj.kill_modbus()


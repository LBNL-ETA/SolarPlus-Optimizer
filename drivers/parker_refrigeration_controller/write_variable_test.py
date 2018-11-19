from modbus_driver import Modbus_Driver
import time
from struct import *

from pymodbus.constants import Endian
from pymodbus.payload import BinaryPayloadDecoder

obj = Modbus_Driver("fridge_config.yaml")
obj.initialize_modbus()

output = obj.get_data()
print("Intital register values:")
print(output)

print("----SETTING SP to 20C-----")
obj.write_register('SP', 20)

#print("----CLEARING HACCP list-----") Writing to this caused error
#obj.write_register('clear_HACCP_historian', 1)

print("----Start Defrost-----")
obj.write_register('defrost_control', 13)

print("wait 5 seconds")
time.sleep(5)

print("Register values after changing the above registers:")
output = obj.get_data()
print(output)


print("----Turn off Defrost-----")
obj.write_register('defrost_control', 12)


obj.kill_modbus()

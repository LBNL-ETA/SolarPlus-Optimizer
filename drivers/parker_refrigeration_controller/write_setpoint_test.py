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

print("----SETTING SP to 33F-----")
obj.write_register('SP', 330)
print("wait 5 seconds")
time.sleep(5)

print("Register values after changing the above registers:")
output = obj.get_data()
print(output)
obj.kill_modbus()

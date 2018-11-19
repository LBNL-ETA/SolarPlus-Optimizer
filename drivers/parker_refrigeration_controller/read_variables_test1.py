from modbus_driver import Modbus_Driver
import time
from struct import *

from pymodbus.constants import Endian
from pymodbus.payload import BinaryPayloadDecoder


obj = Modbus_Driver("fridge_config.yaml")
obj.initialize_modbus()

output = obj.get_data()
print("All Variables:")
print(output)

obj.kill_modbus()

from modbus_driver import Modbus_Driver
import time
from struct import *

from pymodbus.constants import Endian
from pymodbus.payload import BinaryPayloadDecoder


obj = Modbus_Driver("fridge_config.yaml")
obj.initialize_modbus()

print("Cabinet probe register reading:")
print(obj.get_single_register_data(register_name='cab_probe'))

obj.kill_modbus()

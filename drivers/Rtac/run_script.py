from modbus_driver import Modbus_Driver
import time
from struct import *

from pymodbus.constants import Endian
from pymodbus.payload import BinaryPayloadDecoder




obj = Modbus_Driver("bat_driver.yaml",)


obj.initialize_modbus()
output = obj.get_data()
print(output)



obj.kill_modbus()

from modbus_driver import Modbus_Driver
import time
from struct import *

from pymodbus.constants import Endian
from pymodbus.payload import BinaryPayloadDecoder
#TODO make more comprehensive test script for Modbus_Driver()



obj = Modbus_Driver("config.yaml")


obj.initialize_modbus()

output = obj.get_data()
print(output)



obj.kill_modbus()

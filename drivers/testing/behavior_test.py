from modbus_driver import Modbus_Driver
import time
from struct import *

from pymodbus.constants import Endian
from pymodbus.payload import BinaryPayloadDecoder

def set_check(modbus_object,register,set_value):
    modbus_object.write_register(register, set_value)
    assert(modbus_object.read_register(register)==set_value)
    print(register + " was set correctly")

obj = Modbus_Driver("fridge_config.yaml")
obj.initialize_modbus()

# 1. Set the time on the device
# Cannot set the time via modbus as far as I can tell so it must be set manually

# 2. Read the HAACP alarms
print(obj.read_register('HAACP_0_0'))
print(obj.read_register('HAACP_0_1'))
print(obj.read_register('HAACP_0_2'))
# Need to decode the alarms using pack/unpack not sure of the format differentiating
# AL, AH, ld, PF
# Since my screen does not work on my device I cannot differentiate codes on screen

# 3. Clear the HAACP alarms, I was having problems with this on my device
# These registers are write only so they cannot be in the register dictionary
obj.write_data(0x465, 1) # clear_HACCP_historian
obj.write_data(0x490, 1) # clear_HACCP_new_alarm_flag


# 4. Set parameters related to refrigerator control

# working setpoint differential
set_check(obj,'r0',0)

# minimum working setpoint
#obj.write_register('r1', 0)
set_check(obj,'r1',0)

# maximum working setpoint
set_check(obj,'r2',0)
#obj.write_register('r2', 0)

# Measured input for low temperature alarm
# Set 0 for cabinet probe, and 1 for evaporation probe, 2 for auxillary probe
set_check(obj,'A0',1)

# Measured input for high temperature alarm
# Set 0 for cabinet probe and 1 for auxillary probe
set_check(obj,'A3',1)

# Temperature for low temperature alarm to activate values from -99 to 99 C/F
set_check(obj,'A1',-10) # Default is -10

# Temperature for high temperature alarm to activate values from -99 to 99 C/F
set_check(obj,'A4',10) # Default is 10

# Delay for AH after turning on controller, values are from 0-240 minutes
set_check(obj,'A6',120) # Default is 120

# Temperature alarm delay, values are from 0-240 minutes
set_check(obj,'A7',120) # Default is 120

# High temperature alarm delay after the end of the defrost
# (only if A3 = 0 or if P4 = 1 and A3 = 1)
set_check(obj,'A8',15) # Default is 15

# High temperature alarm delay after the deactivation of the microport input
# (only if A3 = 0 or if P4 = 1 and A3 = 1)
set_check(obj,'A9',15) # Default is 15

# Delay recording of power failure alarm
# This one is not related to temperature: AA: delay recording of power failure alarm
set_check(obj,'AA',15) # Default is 1



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
set_check(obj,'d3',0) # Default is 30 (minutes)

 # drip delay
set_check(obj,'d7',30) # Default is 2 (minutes)


# Setpoint
set_check(obj,'SP',0) #  r1 <= SP <= r2, default is zero


output = obj.get_data()
print(output)

obj.kill_modbus()

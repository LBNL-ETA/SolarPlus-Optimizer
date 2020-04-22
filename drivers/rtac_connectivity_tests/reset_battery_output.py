from modbus_driver import Modbus_Driver
import time

obj = Modbus_Driver("rtac_config.yaml",)
obj.initialize_modbus()

output = obj.get_data()
# output = obj.get_data_raw()
print("==========PRINTING CURRENT VALUES: i={} ===========".format(i))
print(output)

## Enter default value here
real_power_output = 0
print("========== WRITING REAL POWER OUTPUT of : i={} ===========".format(real_power_output))
obj.write_register('real_power_setpoint', real_power_output)
# obj.write_register_raw('real_power_setpoint', real_power_output)
print("========== COMPLETED WRITE ===========")

time.sleep(5)

output = obj.get_data()
# output = obj.get_data_raw()
print("==========PRINTING CURRENT VALUES: i={} ===========".format(i))
print(output)
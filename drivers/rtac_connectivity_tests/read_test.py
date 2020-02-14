from modbus_driver import Modbus_Driver
import time

obj = Modbus_Driver("rtac_config.yaml",)

obj.initialize_modbus()
print("current values of the registers")
output = obj.get_data()
print(output)

file_output_name = "read_test_output.csv"

fp = open(file_output_name, "w")
fp.write('time,'+','.join([str(item) for item in output])+'\n')
fp.write(str(time.time())+',' + ','.join([str(item) for item in output.values()]) + '\n')

start_time = time.time()
while (time.time() - start_time) < 60:
    time.sleep(10)
    output = obj.get_data()
    print()
    print(output)
    fp.write(str(time.time())+',' + ','.join([str(item) for item in output.values()]) + '\n')

obj.kill_modbus()
fp.close()



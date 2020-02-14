from modbus_driver import Modbus_Driver
import threading
import time

def continuous_read(obj):
    file_output_name = "discharge_battery_test_output.csv"

    fp = open(file_output_name, 'a')

    i = 0
    try:
        while True:
            output = obj.get_data()
            # output = obj.get_data_raw()
            fp.write(str(time.time()) + ',' + ','.join([str(item) for item in output.values()]) + '\n')

            print("==========PRINTING CURRENT VALUES: i={} ===========".format(i))
            print(output)
            i+=1
            print()

            time.sleep(20)
    except:
        fp.close()


def write_heartbeat(obj):
    i = 0
    heartbeats = [0x55AA, 0xAA55]
    while True:
        print("========== writing heartbeat value = {}".format(heartbeats[i%2]))
        obj.write_register('heartbeat', heartbeats[i % 2])
        # obj.write_register_raw(('heartbeat', heartbeats[i % 2])
        i+=1
        time.sleep(30)

if __name__ == "__main__":
    obj = Modbus_Driver("rtac_config.yaml",)
    obj.initialize_modbus()

    output = obj.get_data()
    # output = obj.get_data_raw()
    print("==========PRINTING CURRENT VALUES: i={} ===========".format(i))
    print(output)
    file_output_name = "discharge_battery_test_output.csv"
    fp = open(file_output_name, 'w')
    fp.write('time,' + ','.join([str(item) for item in output]) + '\n')
    fp.write(str(time.time()) + ',' + ','.join([str(item) for item in output.values()]) + '\n')
    fp.close()

    ## Discharge at 10KW
    real_power_output = -10
    print("========== WRITING REAL POWER OUTPUT of : i={} ===========".format(real_power_output))
    obj.write_register('real_power_setpoint', real_power_output)
    # obj.write_register_raw('real_power_setpoint', real_power_output)
    print("========== COMPLETED WRITE ===========")

    # creating thread
    t1 = threading.Thread(target=continuous_read, args=(obj, ))
    t2 = threading.Thread(target=write_heartbeat(), args=(obj,))

    # starting thread 1
    t1.start()
    # starting thread 2
    t2.start()

    # wait until thread 1 is completely executed
    t1.join()
    # wait until thread 2 is completely executed
    t2.join()

    # both threads completely executed
    print("Done!")
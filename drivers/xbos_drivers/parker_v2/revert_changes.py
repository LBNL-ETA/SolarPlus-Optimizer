from pyxbos.modbus_driver import Modbus_Driver

config_file = "parker_config_v2.yaml"

modbus_device = Modbus_Driver(config_file=config_file, config_section='modbus')
modbus_device.initialize_modbus()

service_name_map = {
    "refrigerator": 0xf7,
    "freezer": 0xf6
}

default_setpoint_map = {
    "refrigerator": 33,
    "freezer": -7
}

register_name = "setpoint"

for device in service_name_map:
    unit = service_name_map[device]
    current_value = round(modbus_device.read_holding_register(register_name=register_name, unit=unit) / 10, 1)
    default_value = default_setpoint_map[device]
    if current_value != default_value:
        value_to_be_written = int(default_value * 10)
        modbus_device.write_register(register_name=register_name, value=value_to_be_written, unit=unit)

        print("device %s, modbus variable=%s, old value = %f, default value = %f, value written=%f" % (device, register_name, current_value, default_value, value_to_be_written))
    else:
        print("no change in setpoint, not changing")

    new_value = round(modbus_device.read_holding_register(register_name=register_name, unit=unit) / 10, 1)
    print("new setpoint = ",new_value)

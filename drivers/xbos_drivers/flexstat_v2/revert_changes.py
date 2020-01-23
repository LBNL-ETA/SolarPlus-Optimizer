import BAC0
import yaml

with open("flexstat_config_v2.yaml") as fp:
    config = yaml.safe_load(fp)

service_name_map = config['xbos']['service_name_map']
thermostat_config = config['thermostat_config']
bacnet_mask = thermostat_config.get('bacnet_network_mask')
bacnet_router_address = thermostat_config.get('bacnet_router_address', None)
bbmd_ttl = thermostat_config.get('bbmd_ttl', None)

if bacnet_router_address == None or bbmd_ttl == None:
    bacnet = BAC0.connect(ip=bacnet_mask)
else:
    bacnet = BAC0.connect(ip=bacnet_mask, bbmdAddress=bacnet_router_address,
                               bbmdTTL=bbmd_ttl)


device_map = {}
for service_name in service_name_map:
    ip = service_name_map[service_name].get('ip')
    device_id = service_name_map[service_name].get('device_id', 1)

    device = BAC0.device(address=ip, device_id=device_id, network=bacnet)
    device_map[service_name] = device

setpoints = {
    "thermostat_east": {
        "OCC HEATING SETPT": 70,
        "OCC COOLING SETPT": 74,
        "UNOCC HEATING SETPT": 66,
        "UNOCC COOLING SETPT": 68
    },
    "thermostat_west": {
        "OCC HEATING SETPT": 70,
        "OCC COOLING SETPT": 75,
        "UNOCC HEATING SETPT": 70,
        "UNOCC COOLING SETPT": 75
    }
}
for service_name in service_name_map:
    bacnet_device = device_map[device]
    setpoints_to_set = setpoints[service_name]

    for sp in setpoints_to_set:
        current_value = bacnet_device[sp]
        value = setpoints_to_set[sp]
        if round(value, 2) != round(current_value, 2):
            bacnet_device[sp].write(value, priority=8)
            print("device = %s setpoint name = %s old value = %f new value = %f"%(service_name, sp, current_value, value))
        else:
            print("device = %s setpoint name = %s value = %f is already default, no need to change" % (service_name, sp, value))

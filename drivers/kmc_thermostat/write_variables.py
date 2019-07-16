from driver import Thermostat

thermostat = Thermostat(config_file = "config.yaml")
interested_points = [
	'SPACE TEMP SENSOR', 
	'ACTIVE HEATING SETPT',
	'ACTIVE COOLING SETPT',
]

for point in interested_points:
	print(thermostat.device[point])


print("SETTING ACTIVE COOLING SETPOINT TO 85")
thermostat.device['ACTIVE COOLING SETPT'] = 85

print("SETTING ACTIVE HEATING SETPOINT TO 65")
thermostat.device['ACTIVE HEATING SETPT'] = 65

for point in interested_points:
	print(thermostat.device[point])

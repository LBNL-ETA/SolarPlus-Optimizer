from driver import Thermostat

thermostat = Thermostat(config_file = "config.yaml")

interested_points = [
	'SPACE TEMP SENSOR', 
	'ACTIVE HEATING SETPT',
	'ACTIVE COOLING SETPT',
	'COOLING NEED',
	'HEATING NEED',
	'COOLING PROP',
	'HEATING PROP',
	'COOLING INTG',
	'HEATING INTG'
]

for point in interested_points:
	print(thermostat.device[point])
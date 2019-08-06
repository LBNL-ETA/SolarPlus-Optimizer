import requests
import yaml
import json

def get_data(ip, device_id, service_id, variable_name):
	url = "http://%s:3480/data_request?id=status&output_format=json&DeviceNum=%d&serviceId=urn:upnp-org:serviceId:%s"%(ip, device_id, service_id)
	device_num = 'Device_Num_%d'%device_id
	temperature_variable = variable_name

	rsp = requests.get(url)
	content = json.loads(rsp.content)
	for state in content[device_num]['states']:
		if state['variable'] == temperature_variable:
			return float(state['value'])

if __name__ == "__main__":
	with open("config.yaml", "r") as fp:
		config = yaml.safe_load(fp)

	device_config = config["device_info"]
	veraplus_ip = device_config['veraplus_ip']
	
	variable_config = config["variables"]

	for variable in variable_config:
		cfg = variable_config[variable]
		val = get_data(ip=veraplus_ip, device_id=cfg['device_id'], service_id=cfg['service_id'], variable_name=cfg['variable_name'])

		print("%s: %f"%(variable, val))

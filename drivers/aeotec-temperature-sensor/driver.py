import requests
import yaml
import json

if __name__ == "__main__":
	with open("config.yaml", "r") as fp:
		config = yaml.safe_load(fp)

	device_config = config["device_info"]
	veraplus_ip = device_config['veraplus_ip']
	device_id = device_config['device_id']
	service_id = device_config['service_id']


	url = "http://%s:3480/data_request?id=status&output_format=json&DeviceNum=%d&serviceId=urn:upnp-org:serviceId:%s"%(veraplus_ip, device_id, service_id)
	device_num = 'Device_Num_%d'%device_id
	
	temperature_variable = device_config["temperature_variable_name"]

	rsp = requests.get(url)
	content = json.loads(rsp.content)
	for state in content[device_num]['states']:
		if state['variable'] == temperature_variable:
			print(state['value'])

import BAC0
import yaml

def init(config):
	device_cfg = config.get('thermostat')
	device_ip = device_cfg.get('device_ip')
	network_mask = device_cfg.get('network_mask')
	device_id = device_cfg.get('device_bacnet_id`')

	bacnet = BAC0.connect(network_mask)
	device = BAC0.device(device_ip, device_id, bacnet)

	return bacnet, device


with open("config.yaml", "r") as fp:
	cfg = yaml.safe_load(fp)
bacnet, device = init(config=cfg)
print(device.points)
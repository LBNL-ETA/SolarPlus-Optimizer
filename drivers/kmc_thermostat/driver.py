import BAC0
import yaml

class Thermostat:

	def __init__(self, config_file, section="thermostat"):
		with open(config_file, "r") as fp:
			config = yaml.safe_load(fp)[section]

		self.device_ip = config.get('device_ip')
		self.network_mask = config.get('network_mask')
		self.device_id = config.get('device_bacnet_id')

		self.bbmd_address = config.get('bbmd_address', None)
		self.bbmd_ttl = config.get('bbmd_ttl', None)

		self.init_bacnet()

	def init_bacnet(self):
		if self.bbmd_address == None or self.bbmd_ttl == None:
			self.bacnet = BAC0.connect(ip=self.network_mask)
		else:
			self.bacnet = BAC0.connect(ip=self.network_mask, bbmdAddress=self.bbmd_address, bbmdTTL=self.bbmd_ttl)

		self.device = BAC0.device(address=self.device_ip, device_id=self.device_id, network=self.bacnet)
		
	def get_points(self):
		points = self.device.points
		return points

	def set_points(self, point_name, value):
		self.device[point_name] = value


if __name__ == "__main__":
	thermostat = Thermostat(config_file = "config.yaml")
	points = thermostat.get_points()

	print(points)
	
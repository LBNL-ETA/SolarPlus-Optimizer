import logging
from pyxbos.process import XBOSProcess, b64decode, schedule, run_loop

# Publish once a day
# Make forecast for two days ahead


class BaselineDriver(XBOSProcess):

	def __init__(self, cfg):
		
		super().__init__(cfg)
		
		# Logging
		self.FORMAT = '%(asctime)-15s %(message)s'
		logging.basicConfig(format=self.FORMAT)
		self.logger = logging.getLogger('DR-SERVER')
		self.logger.setLevel(logging.INFO)

		self.base_resource = cfg['base_resource']
		self.namespace = b64decode(cfg['namespace'])
		
		# Publishing rate
		self._rate = cfg['rate']
		
		# Get baseline data  every _rate seconds and publish
		schedule(self.call_periodic(self._rate, self.read, runfirst=True))


	def get_data_from_influx(self, st, et, agg, measurement, uuid, window):

		q = "select %s(value) as value from %s where \"uuid\"=\'%s\'" % (agg, measurement, uuid)
		
		q += " and time >= '%s' and time <= '%s'" % (st, et)
		""" Below query is more efficienct than the prev one
		res = self.influx_client.query(
            "select last(value), time from timeseries where \"uuid\"=\'%s\' and time > now() - 17m "%uuid)
		"""
		
		q += " group by time(%s)" % (window)

		df = self.influx_client.query(q)[measurement]
		return df

	
	def read(self):

		df_power = get_data_from_influx(st, et, agg, 'timeseries', 
										'd2004400-349c-5015-8f20-e249953295a7', '1min')
		df_weather = get_data_from_influx(st, et, agg, 'timeseries', 
										'f7c1f2c8-c996-528c-ab3d-bdc96dc9cf72', '1min')
		df_dr_signals = get_data_from_influx(st, et, agg, 'timeseries', 
											'a89cfc61-9391-5e3e-b89c-5aa969651eb5', '1min')

		print('df power: ', df_power.head())
		print('df_weather: ', df_weather.head())
		print('df_dr_signals: ', df_dr_signals.head())


if __name__ == '__main__':
	
	parser = argparse.ArgumentParser()
	parser.add_argument('config_file', help='config file')

	args = parser.parse_args()
	config_file = args.config_file

	with open(config_file) as f:
		driverConfig = yaml.safe_load(f)

	logging.basicConfig(level="INFO", format='%(asctime)s - %(name)s - %(message)s')
	baseline_driver = BaselineDriver(driverConfig)
    run_loop()


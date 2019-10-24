import time
from pyxbos.process import XBOSProcess, b64decode, b64encode, schedule, run_loop
from pyxbos import xbos_pb2
from pyxbos import flexstat_pb2
from pyxbos import nullabletypes_pb2 as types
# from pyxbos.energise_pb2 import EnergiseMessage, LPBCStatus, LPBCCommand, SPBC, EnergiseError, EnergisePhasorTarget, ChannelStatus
# from pyxbos.c37_pb2 import Phasor, PhasorChannel
from datetime import datetime
from functools import partial
from collections import deque
import asyncio

class FlexstatDriver(XBOSProcess):

	def __init__(self, cfg):
		super().__init__(cfg)
		self.namespace = b64decode(cfg['namespace'])
		self.device_name = 'test_tstat'
		self._rate = cfg['rate']
		schedule(self.subscribe_extract(self.namespace, "flexstat_test/test_tstat", ".flexstatActuationMessage.setpoints", self._set_setpoints, "set_setpoints"))

		schedule(self.call_periodic(self._rate, self._read_and_publish, runfirst=False))

	def _set_setpoints(self, resp):
		device_name = resp.uri.split('-')[-1]
		print("device_name = ", device_name)


		print(resp.values[0])
		# print(resp.values[0]['coolingSetpoint']['value'])


	async def _read_and_publish(self, *args):


		setpoint_list = []
		for i in range(5):
			setpoint_list.append(
				flexstat_pb2.FlexstatSetpoints(
					change_time = int(time.time()*1e9),
					heating_setpoint = types.Double(value = 20.2 + i),
					cooling_setpoint = types.Double(value = 30.5 + i),
				)
			)
			msg = xbos_pb2.XBOS(
					flexstat_actuation_message = flexstat_pb2.FlexstateActuationMessage(
						time = int(time.time()*1e9),
						setpoints = setpoint_list
						)
					)
			print(msg)
			
			await self.publish(self.namespace, "flexstat_test/test_tstat", msg)

waved = 'localhost:777'
wavemq = 'localhost:4516'
namespace = 'GyA1TN-RJ1DWOjdBV-_2BZDKSH0qOZLeHCwz-Dmpqqy0EA=='
base_resource = 'flexstat_test'
entity = 'flexstat.ent'
driver_id = 'flexstat-test-driver'
rate = 3
thermostat_config = {}

cfg = {
	'waved': waved,
	'wavemq': wavemq,
	'namespace': namespace,
	'base_resource': base_resource,
	'entity': entity,
	'id': driver_id,
	'thermostat_config': {},
	'rate': rate
}
obj = FlexstatDriver(cfg)
run_loop()

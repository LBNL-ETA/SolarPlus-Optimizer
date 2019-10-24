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
		self._set_setpoint_rate = cfg.get("setpoint_rate", 1)
		self._setpoints = []
		schedule(self._query_existing())
		schedule(self.subscribe_extract(self.namespace, "flexstat_test/test_tstat2/actuation", ".flexstatActuationMessage.setpoints", self._save_setpoints, "save_setpoints"))

		schedule(self.call_periodic(self._rate, self._read_and_publish, runfirst=True))
		# schedule(self.call_periodic(self._set_setpoint_rate, self._set_setpoints, runfirst=False))

	async def _query_existing(self):
		msg = await self.query_topic(self.namespace, "flexstat_test/test_tstat2/actuation")
		print(msg)


	def _save_setpoints(self, resp):
		print("inside save")
		device_name = resp.uri.split('-')[-1]
		setpoint_dict = {}
		values = resp.values[0]
		self._setpoints = values
		print("saved setpoints ", self._setpoints)

	async def _set_setpoints(self, *args):
		time_now = time.time()*1e9
		setpoint_dict = self._setpoints
		for setpoint in sorted(setpoint_dict):
			if setpoint < time_now:
				print()
				print("time now = ", time_now)
				print(setpoint_dict[setpoint])
				print()
				break

	async def _read_and_publish(self, *args):
		setpoint_list = []
		time_now = time.time()
		for i in range(5):
			change_time = time_now + i*60
			setpoint_list.append(
				flexstat_pb2.FlexstatSetpoints(
					change_time = int(change_time*1e9),
					heating_setpoint = types.Double(value = 20.2 + 10*i),
					cooling_setpoint = types.Double(value = 30.5 + 10*i),
				)
			)
		msg = xbos_pb2.XBOS(
				flexstat_actuation_message = flexstat_pb2.FlexstatActuationMessage(
					time = int(time_now*1e9),
					setpoints = setpoint_list
					)
				)
		print(msg)
		
		await self.publish(self.namespace, "flexstat_test/test_tstat2/actuation", True, msg)

waved = 'localhost:777'
wavemq = 'localhost:4516'
namespace = 'GyA1TN-RJ1DWOjdBV-_2BZDKSH0qOZLeHCwz-Dmpqqy0EA=='
base_resource = 'flexstat_test'
entity = 'flexstat.ent'
driver_id = 'flexstat-test-driver'
rate = 10
setpoint_rate = 3
thermostat_config = {}

cfg = {
	'waved': waved,
	'wavemq': wavemq,
	'namespace': namespace,
	'base_resource': base_resource,
	'entity': entity,
	'id': driver_id,
	'thermostat_config': {},
	'rate': rate,
	'setpoint_rate': setpoint_rate
}
obj = FlexstatDriver(cfg)
run_loop()

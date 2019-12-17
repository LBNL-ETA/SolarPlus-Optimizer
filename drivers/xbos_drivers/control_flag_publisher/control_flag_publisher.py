from pyxbos.process import XBOSProcess, b64decode, b64encode, schedule, run_loop
from pyxbos import xbos_pb2
from pyxbos import flexstat_pb2
from pyxbos import parker_pb2
from pyxbos import nullabletypes_pb2 as types
import yaml
import argparse
import time
import logging

class ControlFlagPublisher(XBOSProcess):
    def __init__(self, cfg):
        super().__init__(cfg)
        self.config_file = cfg['config_file']
        self.service_name_map = cfg['service_name_map']

        self.namespace = b64decode(cfg['namespace'])
        self._rate = cfg['publish_rate']
        self.service_name_map = {}
        self.publish_times = {}

        schedule(self.call_periodic(self._rate, self.read_and_publish, runfirst=True))

    async def read_and_publish(self, *args):
        with open(self.config_file) as fp:
            config = yaml.safe_load(fp)['xbos'].get('service_name_map', {})

        for topic in config:
            new_flag = config.get(topic)
            publish = False

            if topic in self.service_name_map:
                existing_flag = self.service_name_map[topic]
                if new_flag != existing_flag:
                    publish = True
                    self.service_name_map[topic] = new_flag
                else:
                    if (time.time() - self.publish_times[topic]) >= self._rate:
                        publish = True
            else:
                publish = True
                self.service_name_map[topic] = new_flag

            try:
                if publish:
                    if topic.startswith("flexstat"):
                        msg = xbos_pb2.XBOS(
                            flexstat_actuation_message=flexstat_pb2.FlexstatActuationMessage(
                                time=int(time.time() * 1e9),
                                control_flag=types.Int64(value=new_flag)
                            )
                        )
                    elif topic.startswith("parker"):
                        msg = xbos_pb2.XBOS(
                            parker_actuation_message=parker_pb2.ParkerActuationMessage(
                                time=int(time.time() * 1e9),
                                control_flag=types.Int64(value=new_flag)
                            )
                        )

                    await self.publish(self.namespace, topic, True, msg)
                    print("published %r on topic = %s" % (new_flag, topic))
                    self.publish_times[topic] = time.time()
            except Exception as e:
                print("error occured in pushing control signal to device: %s! error= %r" % (device_type, e))
            print()


parser = argparse.ArgumentParser()
parser.add_argument("config_file", help="config file ")
args = parser.parse_args()
config_file = args.config_file

with open(config_file) as f:
    driverConfig = yaml.safe_load(f)

xbosConfig = driverConfig['xbos']
waved = xbosConfig.get('waved', 'localhost:777')
wavemq = xbosConfig.get('wavemq', 'locahost:4516')
namespace = xbosConfig.get('namespace')
service_name_map = xbosConfig.get('service_name_map')
entity = xbosConfig.get('entity')
rate = xbosConfig.get('publish_rate', 3600)
driver_id = xbosConfig.get('id', 'controlflag-driver')

xbos_cfg = {
	'waved': waved,
	'wavemq': wavemq,
	'namespace': namespace,
	'entity': entity,
	'id': driver_id,
	'publish_rate': rate,
	'service_name_map': service_name_map,
	'config_file': config_file
}

logging.basicConfig(level="INFO", format='%(asctime)s - %(name)s - %(message)s')
obj = ControlFlagPublisher(cfg=xbos_cfg)
run_loop()
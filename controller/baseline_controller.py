import yaml
from influxdb import DataFrameClient
try:
    # xboswave packages
    from pyxbos.eapi_pb2 import *
    from pyxbos.wavemq_pb2 import *
    from pyxbos.wavemq_pb2_grpc import *
    from grpc import insecure_channel
    from pyxbos import xbos_pb2
    from pyxbos import rtac_pb2
    from pyxbos import nullabletypes_pb2 as types
    import base64
except ImportError:
    print("not importing xbos packages")

class Baseline_Controller:
    def __init__(self, config_file="baseline_config.yaml"):
        with open(config_file) as fp:
            self.config = yaml.safe_load(fp)

        self.database_config = self.config.get('database')
        self.xbos_config = self.config.get('xbos')
        self.data_source_config = self.config.get('data_source')
        self.data_sink_config = self.config.get('data_sink')

        self.init_influx(config=self.database_config)
        self.init_xbos(config=self.xbos_config)

    def init_influx(self, config):
        self.influx_client = DataFrameClient(host=config["host"],
                                            port=config["port"],
                                            username=config["username"],
                                            password=config["password"],
                                            ssl=config["ssl"],
                                            verify_ssl=config["verify_ssl"],
                                            database=config["database"])

    def init_xbos(self, config):
        self.entity = open(config.get('entity'), 'rb').read()
        self.perspective = Perspective(
            entitySecret=EntitySecret(DER=self.entity),
        )
        self.namespace = self.ensure_b64decode(config.get('namespace'))
        self.wavemq = config.get('wavemq', 'localhost:4516')
        wavemq_channel = insecure_channel(self.wavemq)
        self.xbos_client = WAVEMQStub(wavemq_channel)
        self.xbos_schema = "xbosproto/XBOS"

   def b64decode(self, e):
        return base64.b64decode(e, altchars=bytes('-_', 'utf8'))

    def ensure_b64decode(self, e):
        return bytes(base64.b64decode(e, altchars=('-_')))
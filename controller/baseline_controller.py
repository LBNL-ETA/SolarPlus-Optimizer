import yaml
from influxdb import DataFrameClient
import base64
import datetime
import pandas as pd
import time

try:
    # xboswave packages
    from pyxbos.eapi_pb2 import *
    from pyxbos.wavemq_pb2 import *
    from pyxbos.wavemq_pb2_grpc import *
    from grpc import insecure_channel
    from pyxbos import xbos_pb2
    from pyxbos import rtac_pb2
    from pyxbos import nullabletypes_pb2 as types
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

        self.init_influx()
        self.init_xbos()

        self.max_battery_rate = self.data_sink_config.get('max_battery_rate', 14000)
        self.min_battery_rate = self.data_sink_config.get('min_battery_rate', -14000)
        self.max_battery_soc = self.data_source_config.get('max_battery_soc', 0.95)
        self.min_battery_soc = self.data_source_config.get('min_battery_soc', 0.25)

    def init_influx(self):
        self.influx_client = DataFrameClient(host=self.database_config["host"],
                                            port=self.database_config["port"],
                                            username=self.database_config["username"],
                                            password=self.database_config["password"],
                                            ssl=self.database_config["ssl"],
                                            verify_ssl=self.database_config["verify_ssl"],
                                            database=self.database_config["database"])

    def b64decode(self, e):
        return base64.b64decode(e, altchars=bytes('-_', 'utf8'))

    def ensure_b64decode(self, e):
        return bytes(base64.b64decode(e, altchars=('-_')))

    def init_xbos(self):
        self.entity = open(self.xbos_config.get('entity'), 'rb').read()
        self.perspective = Perspective(
            entitySecret=EntitySecret(DER=self.entity),
        )
        self.namespace = self.ensure_b64decode(config.get('namespace'))
        self.wavemq = self.xbos_config.get('wavemq', 'localhost:4516')
        wavemq_channel = insecure_channel(self.wavemq)
        self.xbos_client = WAVEMQStub(wavemq_channel)
        self.xbos_schema = "xbosproto/XBOS"

    def get_data(self, start_time, end_time):

        st = start_time.strftime("%Y-%m-%dT%H:%M:%SZ")
        et = end_time.strftime("%Y-%m-%dT%H:%M:%SZ")

        agg = self.data_source_config.get('agg', 'mean')
        window = self.data_source_config.get('window', '5T')
        variable_config = self.data_source_config.get('variables')
        measurement = self.database_config.get('measurement', 'timeseries')

        df_list = []
        column_names = []
        for variable in variable_config:
            uuid = variable_config.get(variable)

            if agg != 'raw':
                q = "select %s(value) as value from %s where \"uuid\"=\'%s\'" % (agg, measurement, uuid)
            else:
                q = "select value from %s where \"uuid\"=\'%s\'" % (measurement, uuid)

            if start_time != None and end_time != None:
                q += " and time >= '%s' and time <= '%s'" % (st, et)
            elif start_time != None:
                q += " and time >= '%s'" % (st)
            elif end_time != None:
                q += " and time <= '%s'" % (et)

            if agg != 'raw':
                q += " group by time(%s)" % (window)

            df = self.influx_client.query(q)[measurement]
            df_list.append(df)
            column_names.append(variable)

        final_df = pd.concat(df_list, axis=1)
        final_df.columns = column_names
        final_df = final_df.tz_localize(None)

        return final_df

    def set_setpoint_xbos(self, df):
        df = df.dropna()
        device_config = self.data_sink_config.get('topic_map')
        for variable in device_config:
            topic = device_config[variable]

            setpoint_list = []
            if topic.startswith("emulated_battery"):
                for index, row in df.iterrows():
                    change_time = int(index.value)
                    real_power_setpoint = row.get('battery_setpoint', None)

                    if real_power_setpoint != None:
                        setpoint = rtac_pb2.RtacSetpoints(change_time=change_time,
                                                          real_power_setpoint=types.Double(value=real_power_setpoint))
                        setpoint_list.append(setpoint)

                if len(setpoint_list) > 0:
                    msg = xbos_pb2.XBOS(
                        rtac_actuation_message=rtac_pb2.RtacActuationMessage(
                            time=int(time.time() * 1e9),
                            setpoints=setpoint_list
                        )
                    )
            print("publishing on to wavemq to topic %s" % (topic))
            self.publish_on_wavemq(topic, msg)

    def publish_on_wavemq(self, uri, *msgs):
        """publishes msgs in list as payload objects"""
        pos = []
        for msg in msgs:
            pos.append(PayloadObject(
                schema = self.xbos_schema,
                content = msg.SerializeToString(),
                ))

        try:
            x = self.xbos_client.Publish(PublishParams(
                perspective=self.perspective,
                namespace=self.namespace,
                uri = uri,
                content = pos,
                persist=True
                ))
            if not x:
                print("Error publishing: {0}".format(x))
            else:
                print("published on wavemq")
        except Exception as e:
            print("Error publishing: {0}".format(e))

    def generate_setpoints(self):
        end_time = datetime.datetime.utcnow()
        start_time = end_time - datetime.timedelta('60T')

        input_df = self.get_data(start_time=start_time, end_time=end_time)
        input_df.resample('60T').mean()

        solar_production = input_df.solar_production.values[0]
        building_load = input_df.building_load.values[0]
        battery_soc = input_df.battery_soc.values[0]

        net_load = building_load - solar_production
        battery_setpoint = 0

        # PV generation > building load, charge the battery
        if net_load < 0:
            # charge if the battery is not full
            if battery_soc < self.max_battery_soc:
                # do not exceed maximum battery rate
                if net_load > self.max_battery_rate:
                    battery_setpoint = self.max_battery_rate
                else:
                    battery_setpoint = net_load
        # PV generation < building load, discharge the battery
        else:
            # discharge battery only if it isn't empty
            if battery_soc > self.min_battery_soc:
                if net_load < self.min_battery_rate:
                    battery_setpoint = self.min_battery_rate
                else:
                    battery_setpoint = net_load
        setpoint_df = pd.DataFrame(data={'battery_setpoint': [battery_setpoint]}, index=end_time)
        self.set_setpoint_xbos(setpoint_df)

if __name__ == '__main__':
    minute = -1
    controller = Baseline_Controller()
    while True:
        time.sleep(1)
        t = datetime.datetime.now()
        print(t)
        if (t.minute in [0,5,10,15,20,25,30,35,40,45,50,55]) and (t.minute != minute):
            minute = t.minute
            try:
                controller.generate_setpoints()
                print('Run ended ok.')
            except Exception as e :
               print('Run ended in error={0}'.format(str(e)))
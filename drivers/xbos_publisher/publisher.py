try:
    from pyxbos.eapi_pb2 import *
    from pyxbos.wavemq_pb2 import *
    from pyxbos.wavemq_pb2_grpc import *
    from grpc import insecure_channel

    import pyxbos.flexstat_pb2 as flexstat_pb2
    import pyxbos.xbos_pb2 as xbos_pb2
    from pyxbos import nullabletypes_pb2 as types
except ImportError:
    print("not importing xbos packages")

import pandas as pd
import time
import datetime
import pytz


def create_setpoints_df(start_date):
    tz_local = pytz.timezone("US/Pacific")
    tz_utc = pytz.timezone("UTC")

    start_time = datetime.time(19, 0, 0)

    start_datetime = datetime.datetime.combine(start_date, start_time)
    print("start: {0}".format(start_datetime))
    end_datetime = start_datetime + datetime.timedelta(hours=14)
    print("end: {0}".format(end_datetime))

    setpoint_df = pd.DataFrame(index=pd.date_range(start=start_datetime, end=end_datetime, freq='5T'))
    setpoint_df = setpoint_df.tz_localize(tz_local)

    setpoint_df['Trtu_west_heat'] = 67
    setpoint_df['Trtu_west_cool'] = 71

    setpoint_df['Trtu_east_heat'] = 70
    setpoint_df['Trtu_east_cool'] = 74

    step1_start_datetime = start_datetime
    step1_end_datetime = step1_start_datetime + datetime.timedelta(hours=4)
    setpoint_df.loc[step1_start_datetime: step1_end_datetime, 'Trtu_west_heat'] = 78
    setpoint_df.loc[step1_start_datetime: step1_end_datetime, 'Trtu_west_cool'] = 82
    setpoint_df.loc[step1_start_datetime: step1_end_datetime, 'Trtu_east_heat'] = 78
    setpoint_df.loc[step1_start_datetime: step1_end_datetime, 'Trtu_east_cool'] = 82

    step2_start_datetime = step1_end_datetime + datetime.timedelta(minutes=5)
    step2_end_datetime = step2_start_datetime + datetime.timedelta(hours=6)
    setpoint_df.loc[step2_start_datetime: step2_end_datetime, 'Trtu_west_heat'] = 61
    setpoint_df.loc[step2_start_datetime: step2_end_datetime, 'Trtu_west_cool'] = 65
    setpoint_df.loc[step2_start_datetime: step2_end_datetime, 'Trtu_east_heat'] = 61
    setpoint_df.loc[step2_start_datetime: step2_end_datetime, 'Trtu_east_cool'] = 65

    setpoint_df = setpoint_df.tz_convert(tz_utc)
    setpoint_df.index.name = 'Time'

    return setpoint_df


def get_wavemq_msg_dictionary(setpoint_df, device_config):
    df = setpoint_df.copy()
    df = df.dropna()

    msg_dict = {}
    for device in device_config:
        var_cfg = device_config[device]

        relevant_df_cols = []
        relevant_new_col_names = []
        for variable in var_cfg:
            df_var_name = var_cfg[variable]
            relevant_df_cols.append(df_var_name)
            relevant_new_col_names.append(variable)

        device_df = df[relevant_df_cols]
        device_df.columns = relevant_new_col_names

        #     print(device_df.head())

        setpoint_list = []
        if device.startswith("flexstat"):
            for index, row in device_df.iterrows():
                change_time = int(index.value)
                hsp = row.get('heating_setpoint', None)
                csp = row.get('cooling_setpoint', None)

                if hsp != None and csp != None:
                    setpoint = flexstat_pb2.FlexstatSetpoints(change_time=change_time,
                                                              heating_setpoint=types.Double(value=hsp),
                                                              cooling_setpoint=types.Double(value=csp))
                elif hsp != None:
                    setpoint = flexstat_pb2.FlexstatSetpoints(change_time=change_time,
                                                              heating_setpoint=types.Double(value=hsp))
                elif csp != None:
                    setpoint = flexstat_pb2.FlexstatSetpoints(change_time=change_time,
                                                              cooling_setpoint=types.Double(value=csp))
                else:
                    setpoint = None

                if setpoint != None:
                    setpoint_list.append(setpoint)
            msg = xbos_pb2.XBOS(
                flexstat_actuation_message=flexstat_pb2.FlexstatActuationMessage(
                    time=int(time.time() * 1e9),
                    setpoints=setpoint_list
                )
            )
            msg_dict[device] = msg

            print("created message to publish on to wavemq to topic %s" % (device))


def publish_on_wavemq(xbos_schema, xbos_client, perspective, namespace, uri, *msgs):
    """publishes msgs in list as payload objects"""
    pos = []
    for msg in msgs:
        pos.append(PayloadObject(
            schema = xbos_schema,
            content = msg.SerializeToString(),
            ))

    try:
        x = xbos_client.Publish(PublishParams(
            perspective=perspective,
            namespace=namespace,
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


start_date = datetime.datetime.now().date()
# start_date = datetime.date(2020, 4, 21)
setpoint_df = create_setpoints_df(start_date)

device_config = {
    "flexstat/thermostat_east/actuation": {"cooling_setpoint": "Trtu_east_cool", "heating_setpoint": "Trtu_east_heat"},
    "flexstat/thermostat_west/actuation": {"cooling_setpoint": "Trtu_west_cool", "heating_setpoint": "Trtu_west_heat"},
}

msg_dictionary = get_wavemq_msg_dictionary(setpoint_df=setpoint_df, device_config=device_config)

xbos_cfg =  {
    "namespace": "",
    "wavemq": "localhost:4516",
    "entity": "data_manager.ent"
}

entity = open(xbos_cfg.get('entity'), 'rb').read()
perspective = Perspective(
    entitySecret=EntitySecret(DER=entity),
)
namespace = ensure_b64decode(xbos_cfg.get('namespace'))
wavemq = xbos_cfg.get('wavemq', 'localhost:4516')
wavemq_channel = insecure_channel(wavemq)
xbos_client = WAVEMQStub(wavemq_channel)
xbos_schema = "xbosproto/XBOS"

for topic in msg_dictionary:
    msg = msg_dictionary[topic]
    try:
        publish_on_wavemq(xbos_schema=xbos_schema, xbos_client=xbos_client, perspective=perspective, namespace=namespace,
                      uri=topic, msg=msg)
        print("successfully published to topic={0}".format(topic))
    except Exception as e:
        print("Error while publishing on topic={0} error={1}".format(topic, str(e)))




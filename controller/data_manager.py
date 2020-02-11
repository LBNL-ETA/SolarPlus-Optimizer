import pandas as pd
import pytz
import datetime
import os
from influxdb import DataFrameClient
import yaml
import requests
import json
import time

try:
    # xboswave packages
    from pyxbos.eapi_pb2 import *
    from pyxbos.wavemq_pb2 import *
    from pyxbos.wavemq_pb2_grpc import *
    from grpc import insecure_channel
    from pyxbos import xbos_pb2
    from pyxbos import flexstat_pb2
    from pyxbos import parker_pb2
    from pyxbos import nullabletypes_pb2 as types
    import base64
except ImportError:
    print("not importing xbos packages")

class Data_Manager():

    def __init__(self, data_path="data", data_manager_config=None):
        '''Constructor

            Parameters
            ----------
            data_path: str
                folder name in the root directory of the repository where the data files are located

            data_manager_config: dict
                configuration dict for data_manager
        '''
        self.data_manager_config = data_manager_config

        self.data_path = data_path + "/"

        for source_type in self.data_manager_config["source"]:
            if source_type == "csv_files":
                self.files = self.data_manager_config["source"][source_type]
                self.init_csv(files=self.files)
            elif source_type == "influxdb":
                with open(self.data_manager_config["source"][source_type]["config_filename"], "r") as fp:
                    self.influx_cfg = yaml.safe_load(fp)[self.data_manager_config["source"][source_type]["section"]]
                self.init_influx(influx_cfg=self.influx_cfg)
            elif source_type == "xbos":
                self.xbos_cfg = self.data_manager_config["source"]["xbos"]
                self.init_xbos(xbos_cfg=self.xbos_cfg)


        self.data_sink = self.data_manager_config["data_sink"]
        self.site = self.data_manager_config["site"]

        self.tz_local = pytz.timezone("America/Los_Angeles")
        self.tz_utc = pytz.timezone("UTC")

    def init_influx(self, influx_cfg):
        '''Initialize influxdb client

            Parameters
            ----------
            influx_cfg: dict()
                influxdb configuration dictionary

            Returns
            -------
            None
        '''
        self.influx_client = DataFrameClient(host=influx_cfg["host"],
                                            port=influx_cfg["port"],
                                            username=influx_cfg["username"],
                                            password=influx_cfg["password"],
                                            ssl=influx_cfg["ssl"],
                                            verify_ssl=influx_cfg["verify_ssl"],
                                            database=influx_cfg["database"])

    def init_xbos(self, xbos_cfg):
        '''Initialize xbos client

            Parameters
            ----------
            xbos_cfg: dict()
                xbos configuration dictionary

            Returns
            -------
            None
        '''
        # self.xbos_url = xbos_cfg.get('web_server_url', None)
        # self.xbos_req_headers = {'Content-Type': 'application/json'}

        self.entity = open(xbos_cfg.get('entity'), 'rb').read()
        self.perspective = Perspective(
            entitySecret=EntitySecret(DER=self.entity),
        )
        self.namespace = self.ensure_b64decode(xbos_cfg.get('namespace'))
        self.wavemq = xbos_cfg.get('wavemq', 'localhost:4516')
        wavemq_channel = insecure_channel(self.wavemq)
        self.xbos_client = WAVEMQStub(wavemq_channel)
        self.xbos_schema = "xbosproto/XBOS"


    def init_csv(self, files):
        '''For all the csv files in the config["csv_files"], get a dictionary of dataframes {filename, DataFrame, ..}

            Parameters
            ----------
            None

            Returns
            -------
            None

        '''
        for file in files:
            filename = self.data_path + file
            if not os.path.exists(filename):
                raise Exception("file {0} does not exist in folder {1}".format(file, self.data_path))

    def b64decode(self, e):
        return base64.b64decode(e, altchars=bytes('-_', 'utf8'))

    def ensure_b64decode(self, e):
        return bytes(base64.b64decode(e, altchars=('-_')))

    def get_single_data_from_influx(self, uuid, measurement='timeseries', start_time=None, end_time=None, window='5m', agg='mean', forecast=False):
        '''From the influxdb measurement, get one particular variable as a DataFrame
               Parameters
               ----------
               measurement: string
                   measurement which contains the variable to be queried
               variable: string
                   variable being queried
               start_time : datetime
                   Start time of timeseries
               end_time : datetime
                   End time of timeseries

               Returns
               -------
               df: pandas DataFrame
                   DataFrame where the column is the variable being queried
           '''

        if start_time != None:
            st = start_time.strftime("%Y-%m-%dT%H:%M:%SZ")
            st_hour = datetime.datetime.combine(start_time.date(), datetime.time(start_time.hour, 0, 0, tzinfo=start_time.tzinfo))

        if end_time != None:
            et = end_time.strftime("%Y-%m-%dT%H:%M:%SZ")
            et_hour = datetime.datetime.combine(end_time.date(), datetime.time(end_time.hour, 0, 0, tzinfo=start_time.tzinfo)) + datetime.timedelta(hours=1)

        if forecast:
            latest_ts = self.get_last_ts_influx(uuid=uuid)
            q = "select prediction_time, value from %s where \"uuid\"=\'%s\'" % (measurement, uuid)
            q += " and time= " + (str(latest_ts))
            df = self.influx_client.query(q)[measurement]
            df = df[['prediction_time', 'value']]
            df.prediction_time = pd.to_datetime(df.prediction_time.astype(int) * 1e9)
            df = df.sort_values(by='prediction_time').set_index('prediction_time').tz_localize(self.tz_utc)
            df.index.name = 'time'
            if start_time != None and end_time != None:
                # df = df[st_hour: end_time]
                df = df[st_hour: et_hour]
            elif start_time != None:
                df = df[st_hour:]
            elif end_time != None:
                # df = df[:end_time]
                df = df[:et_hour]

            if agg != 'raw':
                window = window.replace("m", "T")
                df = df[st_hour:et_hour].resample(window).agg(agg).interpolate(method='linear')
                df = df[start_time:end_time]
        else:
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
        return df

    def get_single_data_from_csv(self, filename, column_name, start_time=None, end_time=None, tz="America/Los_Angeles", agg='mean', window='5m'):
        if start_time != None:
            st_hour = datetime.datetime.combine(start_time.date(), datetime.time(start_time.hour, 0, 0, tzinfo=start_time.tzinfo))

        file_tz = pytz.timezone(tz)
        window = window.replace('m', 'T')
        df = pd.read_csv(self.data_path + filename, index_col=0, parse_dates=True)
        df = df.tz_localize(file_tz).tz_convert(self.tz_utc)
        df.index = pd.to_datetime(df.index)

        if start_time != None and end_time != None:
            idx = df.loc[st_hour: end_time].index
            df = df.loc[idx, column_name]
        elif start_time != None:
            idx = df.loc[st_hour:].index
            df = df.loc[idx, column_name]
        elif end_time != None:
            idx = df.loc[:end_time].index
            df = df.loc[idx, column_name]
        else:
            df = df.loc[:, column_name]

        if agg != 'raw':
            df = df.resample(window).agg(agg).interpolate(method='linear')[start_time:end_time]
        df = df.dropna()

        return df

    def get_last_ts_influx(self, uuid, measurement='timeseries'):
        '''Query influx forecast table to retrieve the timestamp of the latest forecast

         Parameters
            ----------
            uuid: str
                uuid of the variable we're interested in
            measurement: str
                measurement to find the latest forecast from. default measurement = timeseries

            Returns
            -------
            ts: int
                latest timestamp when the forecasts came in
        '''
        res = self.influx_client.query(
            "select last(value), time from timeseries where \"uuid\"=\'%s\' and time > now() - 17m "%uuid)
        if not measurement in res:
            res = self.influx_client.query(
                "select last(value), time from timeseries where \"uuid\"=\'%s\' " % uuid)
        return res[measurement].index.values[0].astype('uint64')

    def get_timeseries_from_config(self, config, start_time=None, end_time=None, forecast=False):
        '''From the configuration dictionary, get a DataFrame of all the variables in the variable map
           For all the csv files in the config["csv_files"], get a dictionary of dataframes {filename, DataFrame, ..}

            Parameters
            ----------
            config: section name in config file ("weather"/"price"/"control"/"constraint"/"system")
                pointer to individual configuration sections for weather, price, control etc.
            start_time : datetime in UTC
                Start time of timeseries
            end_time : datetime in UTC
                End time of timeseries

            Returns
            -------
            df: DataFrame
                DataFrame, whose each column is the timeseries of the variables in data_manager_config[config]["variables"]

        '''
        section_config = self.data_manager_config[config]
        section_type = section_config.get("type", None)
        variables = section_config["variables"]
        df_list = []
        column_names = []

        for variable in variables:
            variable_cfg = variables[variable]
            source_type = variable_cfg.get("type", section_type)

            if source_type == "csv":
                filename = variable_cfg.get('filename')
                column_name = variable_cfg.get('column')
                tz = variable_cfg.get('tz', 'America/Los_Angeles')
                agg = variable_cfg.get('agg', 'mean')
                window = variable_cfg.get('window', '5m')

                df = self.get_single_data_from_csv(filename=filename, column_name=column_name, start_time=start_time, end_time=end_time, tz=tz, agg=agg,
                                                   window=window)
                df_list.append(df)
                column_names.append(variable)
            elif source_type == "influxdb":
                uuid = variable_cfg.get('uuid')
                window = variable_cfg.get('window', '5m')
                agg = variable_cfg.get('agg', 'mean')
                measurement = variable_cfg.get('measurement', 'timeseries')

                df = self.get_single_data_from_influx(uuid=uuid, measurement=measurement, start_time=start_time,
                                                      end_time=end_time, window=window, agg=agg, forecast=forecast)
                df_list.append(df)
                column_names.append(variable)

        final_df = pd.concat(df_list, axis=1)
        final_df.columns = column_names
        final_df = final_df.tz_localize(None)

        return final_df

    def get_data_from_config(self, config, start_time=None, end_time=None, forecast=None):
        '''Get config file from mpc and retrieve required variables

            Parameters
            ----------
            config: section name in config file ("weather"/"price"/"control"/"constraint"/"system")
                pointer to individual configuration sections for weather, price, control etc.
            start_time : datetime in UTC
                Start time of timeseries
            end_time : datetime in UTC
                End time of timeseries

            Returns
            -------
            df: DataFrame
                DataFrame, whose each column is the timeseries of the variables in config['vm']

        '''
        if forecast == None:
            forecast = False
            if config == "weather" or config == "price" or config == "constraint":
                forecast = True
        df = self.get_timeseries_from_config(config=config, start_time=start_time, end_time=end_time, forecast=forecast)
        return df

    def init_data_from_config(self, config):
        '''Get config file from mpc and retrieve required variables

            Parameters
            ----------
            config: section name in config file ("weather"/"price"/"control"/"constraint"/"system")
                pointer to individual configuration sections for weather, price, control etc.

            Returns
            -------
            df: DataFrame
                an empty dataFrame, whose each column is the timeseries of the variables in config['vm']

        '''
        section_config = self.data_manager_config[config]
        variables = list(section_config["variables"].keys())
        return pd.DataFrame(columns=variables)

    def write_df_to_csv(self, df, filename, overwrite=True):
        '''Write df to csv: if file exists, append; else create new file

            Parameters
            ----------
            df: DataFrame
                DataFrame, whose each column has to be written to csv
            filename: str
                path and name of the csv file the df is written to

            Returns
            -------
            None

        '''
        if not overwrite:
            if os.path.exists(filename):
                existing_df = pd.read_csv(filename, index_col=0, parse_dates=True)
                new_df = pd.concat([existing_df, df], axis=0)
                new_df.to_csv(filename)
            else:
                df.to_csv(filename)
        else:
            df.to_csv(filename)

    def write_df_to_influx(self, df, influx_dataframe_client, measurement):
        '''Write df to influx: overwrites if timestamp already exists for each column

            Parameters
            ----------
            df: DataFrame
                DataFrame, whose each column has to be written to influx
            influx_dataframe_client: influxdb.DataFrameClient
                client to send/receive data to/from influxdb
            measurement: str
                name of measurement to store the values

            Returns
            -------
            None

        '''
        df.index.name = 'time'
        df_to_send = []
        for col in df.columns:
            df2 = df[[col]]
            df2.columns = ['value']
            df2['name'] = col
            df2 = df2.dropna()
            df2['value'] = df2['value'].astype(float)
            df_to_send.append(df2)
        df = pd.concat(df_to_send, axis=0)
        influx_dataframe_client.write_points(dataframe=df, measurement=measurement, tag_columns=['name'],
                                        field_columns=['value'])

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

    def set_setpoints_xbos(self, df, device_config):
        df = df.dropna()
        for device in device_config:
            var_cfg = device_config[device]
            # var_cfg = {"cooling_setpoint": "Trtu_east_cool", "heating_setpoint": "Trtu_east_heat"}

            relevant_df_cols = []
            relevant_new_col_names = []
            for variable in var_cfg:
                df_var_name = var_cfg[variable]
                relevant_df_cols.append(df_var_name)
                relevant_new_col_names.append(variable)

            device_df = df[relevant_df_cols]
            device_df.columns = relevant_new_col_names

            # df.columns = [cols[col] if col in cols.keys() else col for col in df.columns]

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
                    elif hsp!=None:
                        setpoint = flexstat_pb2.FlexstatSetpoints(change_time=change_time,
                                                                  heating_setpoint=types.Double(value=hsp))
                    elif csp!=None:
                        setpoint = flexstat_pb2.FlexstatSetpoints(change_time=change_time,
                                                                  cooling_setpoint=types.Double(value=csp))
                    else:
                        setpoint = None

                    if setpoint != None:
                        setpoint_list.append(setpoint)
                msg = xbos_pb2.XBOS(
                    flexstat_actuation_message=flexstat_pb2.FlexstatActuationMessage(
                        time=int(time.time() * 1e9),
                        setpoints = setpoint_list
                    )
                )
            elif device.startswith("parker"):
                for index, row in device_df.iterrows():
                    change_time = int(index.value)
                    device_setpoint = row.get('setpoint', None)
                    differential = row.get('differential', None)

                    if device_setpoint != None and differential!=None:
                        setpoint = parker_pb2.ParkerSetpoints(change_time=change_time,
                                                              setpoint=types.Double(value=device_setpoint),
                                                              differential=types.Double(value=differential))
                    elif device_setpoint!=None:
                        setpoint = parker_pb2.ParkerSetpoints(change_time=change_time,
                                                              setpoint=types.Double(value=device_setpoint))
                    elif differential!=None:
                        setpoint = parker_pb2.ParkerSetpoints(change_time=change_time,
                                                              differential=types.Double(value=differential))
                    else:
                        setpoint=None

                    if setpoint != None:
                        setpoint_list.append(setpoint)

                msg = xbos_pb2.XBOS(
                    parker_actuation_message=parker_pb2.ParkerActuationMessage(
                        time=int(time.time() * 1e9),
                        setpoints = setpoint_list
                    )
                )
            print("publishing on to wavemq to topic %s"%(device))
            self.publish_on_wavemq(device, msg)

    def set_setpoints(self, df):
        '''Set following variables: uCharge, uDischarge, Trtu, Tref, Tfre, Trtu_cool, Trtu_heat

            Parameters
            ----------
            df: DataFrame
                DataFrame, whose each column has to be written to a settings.csv

            Returns
            -------
            None

        '''
        #TODO: include push to devices when ready
        for source_type in self.data_sink["setpoints"]["type"].split('|'):
            if source_type == "csv":
                filename = self.data_path + self.data_sink["setpoints"]["filename"]
                self.write_df_to_csv(df=df, filename=filename)
            elif source_type == "influxdb":
                measurement = self.data_sink["setpoints"]["measurement"]
                self.write_df_to_influx(df=df, influx_dataframe_client=self.influx_client, measurement=measurement)
            elif source_type == "xbos":
                device_config = self.data_sink["setpoints"]["devices"]
                self.set_setpoints_xbos(df=df, device_config=device_config)

    def set_data(self, df):
        '''Set one or more columns in the dataframe to corresponding destinations in data_sink

            Parameters
            ----------
            df: DataFrame
                DataFrame, whose each column has to be written to a destination

            Returns
            -------
            None

        '''
        csv_file_var_map = {}
        influxdb_var_map = {}
        sink_variables = self.data_sink["variables"]
        for var in df.columns:
            for source_type in sink_variables[var]["type"].split('|'):
                if source_type == "csv":
                    filename = sink_variables[var]["filename"]
                    vars = csv_file_var_map.get(filename, [])
                    vars.append(var)
                    csv_file_var_map[filename] = vars
                elif source_type == "influxdb":
                    measurement = sink_variables[var]["measurement"]
                    vars = influxdb_var_map.get(measurement, [])
                    vars.append(var)
                    influxdb_var_map[measurement] = vars

        for file in csv_file_var_map:
            cols = csv_file_var_map[file]
            part_df = df[[cols]]
            name = self.data_path + file
            self.write_df_to_csv(df=part_df, filename=name)

        for measurement in influxdb_var_map:
            cols = influxdb_var_map[measurement]
            part_df = df[[cols]]
            self.write_df_to_influx(df=part_df, influx_dataframe_client=self.influx_client, measurement=measurement)

import pandas as pd
import datetime
import os
from influxdb import DataFrameClient
import yaml
import requests

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
        # TODO: handle timezones
        self.data_manager_config = data_manager_config

        for source_type in self.data_manager_config["source"]:
            if source_type == "csv_files":
                self.files = self.data_manager_config["source"][source_type]
            elif source_type == "influxdb":
                with open(self.data_manager_config["source"][source_type]["config_filename"], "r") as fp:
                    self.influx_cfg = yaml.safe_load(fp)[self.data_manager_config["source"][source_type]["section"]]
                self.init_influx(influx_cfg=self.influx_cfg)
            elif source_type == "xbos":
                with open(self.data_manager_config["source"][source_type]["config_filename"], "r") as fp:
                    self.xbos_cfg = yaml.safe_load(fp)[self.data_manager_config["source"][source_type]["section"]]
                self.init_xbos(xbos_cfg=self.xbos_cfg)

        self.data_from_csvs = {}
        self.data_path = data_path + "/"
        self.data_sink = self.data_manager_config["data_sink"]
        self.site = self.data_manager_config["site"]

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
        self.xbos_url = xbos_cfg['web_server_url']
        self.xbos_req_headers = {'Content-Type': 'application/json'}

    def get_all_csv_data(self):
        '''For all the csv files in the config["csv_files"], get a dictionary of dataframes {filename, DataFrame, ..}

            Parameters
            ----------
            None

            Returns
            -------
            None

        '''
        for file in self.files:
            filename = self.data_path + file
            if os.path.exists(filename):
                self.data_from_csvs[file] = pd.read_csv(filename, index_col=0, parse_dates=True)

    def get_single_data_from_influx(self, measurement, variable, start_time=None, end_time=None):
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

        # TODO: handle start_time, end_time

        q = "select value from %s where \"name\"=\'%s\'" % (measurement, variable)
        df = self.influx_client.query(q)[measurement]
        df.columns = variable
        return df

    def check_if_valid_measurement(self, influx_client, measurement):
        '''Check if measurement exists in influxdb database or if it is not empty

            Parameters
            ----------
            influx_client: influxdb.DataFrameClient
                client to send/receive data to/from influxdb
            measurement: str
                check if this measurement is valid

            Returns
            -------
            flag: bool
                True if measuremnet exists and has data, otherwise False
        '''
        response = influx_client.query("select * from {}".format(measurement))
        if response == {}:
            return False
        else:
            return True

    def get_section_data_from_influx(self, config, influx_client, start_time=None, end_time=None):
        '''From the configuration dictionary, get a DataFrame of all the variables from influxdb

            Parameters
            ----------
            config: dict()
                individual configuration sections for weather, price, control etc.
            influx_client: influxdb.DataFrameClient
                client to send/receive data to/from influxdb
            start_time : datetime
                Start time of timeseries
            end_time : datetime
                End time of timeseries

            Returns
            -------
            df: pandas DataFrame
                DataFrame where each column is a variable in the variables section in the configuration
        '''

        # TODO: handle start_time, end_time
        measurement = config["measurement"]
        if not self.check_if_valid_measurement(influx_client=influx_client, measurement=measurement):
            return pd.DataFrame()
        variables = config["variables"].keys()

        df_list = []
        column_names = []
        for variable in variables:
            q = "select value from %s where \"name\"=\'%s\'"%(measurement, variable)
            df = influx_client.query(q)[measurement]
            df.index = df.index.tz_localize(None)
            df_list.append(df)
            column_names.append(config["variables"][variable])
        final_df = pd.concat(df_list, axis=1)
        final_df.columns = column_names
        return final_df

    def get_section_data_from_xbos(self, config, xbos_client, window='5m', start_time=None, end_time=None):
        '''From the configuration dictionary, get a DataFrame of all the variables from influxdb

            Parameters
            ----------
            config: dict()
                individual configuration sections for weather, price, control etc.
            xbos_client: MortarClient
                client to query data via xbos
            start_time : datetime
                Start time of timeseries
            end_time : datetime
                End time of timeseries

            Returns
            -------
            df: pandas DataFrame
                DataFrame where each column is a variable in the variables section in the configuration
        '''


        measurement = config["measurement"]
        if not self.check_if_valid_measurement(influx_client=influx_client, measurement=measurement):
            return pd.DataFrame()
        variable_cfg = config["variables"]
        variables = variable_cfg.keys()

        df_list = []
        column_names = []
        for variable in variables:
            req_data = variable_cfg[variable].copy()
            start = start_time.strftime("%Y-%m-%dT%H:%M:%SZ")
            end = end_time.strftime("%Y-%m-%dT%H:%M:%SZ")
            sites = [self.site]

            req_data.update(
                {
                    "site": sites,
                    "start": start,
                    "end": end
                }
            )
            rsp = requests.get(self.xbos_url, headers=self.xbos_req_headers, data=json.dumps(req_data))
            if rsp.statusCode == 200:
                op = json.loads(rsp.json()["data"])
                df = pd.DataFrame(op)
                df.index = pd.to_datetime(df.index, unit='ms')
                # TODO: handle timzones
                # df.index = df.index.tz_localize(None)
            else:
                df = pd.DataFrame()

            df_list.append(df)
            column_names.append(variable)

        final_df = pd.concat(df_list, axis=1)
        final_df.columns = column_names
        return final_df

    def find_file_from_variable(self, variable):
        '''Find which file the variable belongs to, by checking column names of each csv file

            Parameters
            ----------
            variable: str
                variable name

            Returns
            -------
            file: str
                filename of the csv file in which the variable is present or None, if variable not found in any file
        '''
        for file in self.files:
            if variable in self.data_from_csvs[file].columns:
                return file
        return None

    def get_timeseries_from_config(self, config, start_time=None, end_time=None):
        '''From the configuration dictionary, get a DataFrame of all the variables in the variable map
           For all the csv files in the config["csv_files"], get a dictionary of dataframes {filename, DataFrame, ..}

            Parameters
            ----------
            config: section name in config file ("weather"/"price"/"control"/"constraint"/"system")
                pointer to individual configuration sections for weather, price, control etc.
            start_time : datetime
                Start time of timeseries
            end_time : datetime
                End time of timeseries

            Returns
            -------
            df: DataFrame
                DataFrame, whose each column is the timeseries of the variables in data_manager_config[config]["variables"]

        '''
        # TODO: handle st, et for influx and XBOS versions
        # if start_time!=None and end_time!=None:
        #     # get data for that time period
        df_list = []
        column_names = []
        section_config = self.data_manager_config[config]
        variables = section_config["variables"].keys()
        source = section_config["type"]

        if source == "csv":
            for variable in variables:
                file = self.find_file_from_variable(variable)
                if file == None:
                    print('variable %s'%variable)
                else:
                    column_names.append(section_config["variables"][variable])
                    df_list.append(self.data_from_csvs[file][[variable]])
            df = pd.concat(df_list, axis=1)
            df.columns = column_names

        elif source == "influxdb":
            df = self.get_section_data_from_influx(config=section_config, influx_client=self.influx_client)

        elif source == "xbos":
            df = self.get_section_data_from_xbos(config=section_config, xbos_client =self.xbos_client, start_time=start_time, end_time=end_time)


        # df.index = pd.to_datetime(df.index, utc=True)
        # return df.loc[start_time: end_time]
        return df

    def get_data(self, variable_list, start_time=None, end_time=None):
        '''Return a DataFrame of all the variables in the variable_list

            Parameters
            ----------
            variable_list: list
                list of variable names
            start_time : datetime
                Start time of timeseries
            end_time : datetime
                End time of timeseries

            Returns
            -------
            df: DataFrame
                DataFrame, whose each column is the timeseries of the variables in variable_list

        '''
        # TODO: handle st, et for influx and XBOS versions
        # if st!=None and et!=None:
        #     # get data for that time period
        self.get_all_csv_data()
        df_list = []

        if type(variable_list) == str:
            variable_list = [variable_list]

        for variable in variable_list:
            file = self.find_file_from_variable(variable)
            if file != None:
                df = self.data_from_csvs[file][[variable]]
                df_list.append(df)
            else:
                df_list.append(pd.DataFrame())

        return pd.concat(df_list, axis=1)

    def get_data_from_config(self, config, start_time=None, end_time=None):
        '''Get config file from mpc and retrieve required variables

            Parameters
            ----------
            config: section name in config file ("weather"/"price"/"control"/"constraint"/"system")
                pointer to individual configuration sections for weather, price, control etc.
            start_time : datetime
                Start time of timeseries
            end_time : datetime
                End time of timeseries

            Returns
            -------
            df: DataFrame
                DataFrame, whose each column is the timeseries of the variables in config['vm']

        '''
        self.get_all_csv_data()
        df = self.get_timeseries_from_config(config=config, start_time=start_time, end_time=end_time)
        return df

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

import pandas as pd
import datetime
import os

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
        self.files = self.data_manager_config["source"]["csv_files"]
        self.data_from_csvs = {}
        self.data_path = data_path + "/"
        self.data_sink = self.data_manager_config["data_sink"]

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

    '''

        returns: filename, if found; else None
    '''
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
        '''From the configuration dictionary, get a DataFrame of all the variables in the variable mapFor all the csv files in the config["csv_files"], get a dictionary of dataframes {filename, DataFrame, ..}

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

        for variable in variables:
            if source == "csv":
                file = self.find_file_from_variable(variable)
                if file == None:
                    print('variable %s'%variable)
                else:
                    column_names.append(section_config["variables"][variable])
                    df_list.append(self.data_from_csvs[file][[variable]])

        df = pd.concat(df_list, axis=1)
        df.columns = column_names
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
        if self.data_sink["setpoints"]["type"] == "csv":
            filename = self.data_path + self.data_sink["setpoints"]["filename"]
            self.write_df_to_csv(df=df, filename=filename)

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
        sink_variables = self.data_sink["variables"]
        for var in df.columns:
            if sink_variables[var]["type"] == csv:
                filename = sink_variables[var]["filename"]
                vars = csv_file_var_map.get(filename, [])
                vars.append(var)
                csv_file_var_map[filename] = vars

        for file in csv_file_var_map:
            cols = csv_file_var_map[file]
            part_df = df[[cols]]
            name = self.data_path + file
            self.write_df_to_csv(df=part_df, filename=name)

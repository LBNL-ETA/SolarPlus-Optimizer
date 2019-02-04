import pandas as pd
import mpc_config
import numpy as np
import datetime


class Data_Manager():

    def __init__(self, data_path="data"):
        '''Constructor

            Parameters
            ----------
            data_path: str
                folder name in the root directory of the repository where the data files are located
        '''
        # TODO: handle timezones
        self.config = mpc_config.get_config()
        self.files = self.config["csv_files"]
        self.data_from_csvs = {}
        self.data_path = data_path + "/"



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
            self.data_from_csvs[file] = pd.read_csv(self.data_path + file, index_col=0, parse_dates=True)

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
            config: dict()
                individual configuration sections for weather, price, control etc.
            start_time : datetime
                Start time of timeseries
            end_time : datetime
                End time of timeseries

            Returns
            -------
            df: DataFrame
                DataFrame, whose each column is the timeseries of the variables in config['vm']

        '''
        # TODO: handle st, et for influx and XBOS versions
        # if start_time!=None and end_time!=None:
        #     # get data for that time period
        df_list = []
        for variable in config["vm"]:
            source = config["type"]
            if source == "csv":
                file = self.find_file_from_variable(variable)
                df_list.append(self.data_from_csvs[file][[variable]])

        df = pd.concat(df_list, axis=1)
        # df.index = pd.to_datetime(df.index, utc=True)
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


    def modify_control_df(self, df_power, pre_fix=False):
        '''This function takes the dataframe of power values and processes it to add more columns relevant to MPCPy

            Parameters
            ----------
            df_power: DataFrame
                DataFrame of power consumption values, columns=['FreComp', 'RefComp', 'HVAC1']
            pre_fix : bool
                determines the power limit on freezer compressor

            Returns
            -------
            df: DataFrame
                A processed DataFrame, columns=['FreComp', 'RefComp', 'HVAC1', 'Defrost', 'FreComp_Split',
                    'FreHeater_Split', 'FreComp_Split_Norm', 'FreHeater_Split_Norm',
                    'RefComp_Norm', 'HVAC1_Norm', 'uHeat', 'uCharge', 'uDischarge']

        '''
        if pre_fix:
            fre_comp_lim = 600
        else:
            fre_comp_lim = 6000

        df_power.index = pd.to_datetime(df_power.index.values)
        # Initialize new column
        df_power['Defrost'] = np.where(df_power['FreComp'] > fre_comp_lim, True, False)
        # Find when each defrost cycle starts
        times = []
        skip = False
        for time in df_power.index:
            if (df_power['FreComp'].loc[time] > fre_comp_lim) and (not skip):
                times.append(time)
                skip = True
            elif (df_power['FreComp'].loc[time] <= fre_comp_lim):
                skip = False
        for time in times:
            if (time - times[-1] <= datetime.timedelta(minutes=20)):
                df_power['Defrost'].loc[time:time + datetime.timedelta(minutes=20)] = True

        df_power['FreComp_Split'] = np.where(df_power['Defrost'] == True, 0, df_power['FreComp'])
        df_power['FreHeater_Split'] = np.where(df_power['Defrost'] == True, df_power['FreComp'], 0)

        # Normalize to [0,1]
        for key in ['FreComp_Split', 'FreHeater_Split', 'RefComp', 'HVAC1']:
            key_new = key + '_Norm'
            df_power[key_new] = df_power[key] / df_power[key].max()
            if 'HVAC' in key:
                df_power[key_new] = np.round(df_power[key_new] * 2) / 2
            else:
                df_power[key_new] = np.round(df_power[key_new])

        df_power['uHeat'] = 0
        df_power['uCharge'] = 0
        df_power['uDischarge'] = 0

        df_power.index.name = 'Time'
        return df_power

    def get_data_from_config(self, config, start_time=None, end_time=None):
        '''

            Parameters
            ----------
            config: dict()
                individual configuration sections for weather, price, control etc. (required keys: path, vm and type)
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
        if config['path'] == 'data/Control2.csv':
            return self.modify_control_df(df_power=df)
        return df

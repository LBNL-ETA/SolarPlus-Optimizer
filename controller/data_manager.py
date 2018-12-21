import pandas as pd
import mpc_config
import numpy as np
import datetime


class Data_Manager():

    def __init__(self, data_path="data"):
        # TODO: handle timezones
        self.config = mpc_config.get_config()
        self.files = self.config["csv_files"]
        self.data_from_csvs = {}
        self.data_path = data_path + "/"

        self.get_all_csv_data()

    '''
        for all the csv files in the config["csv_files"], get dataframes
        self.data_from_csvs: dictionary of {filename: DataFrame, ..}
    '''
    def get_all_csv_data(self):
        for file in self.files:
            self.data_from_csvs[file] = pd.read_csv(self.data_path + file, index_col=0, parse_dates=True)

    '''
        find which file the variable belongs to: check column names of each dataframe in self.data_from_csvs
        returns: filename, if found; else None 
    '''
    def find_file_from_variable(self, variable):
        for file in self.files:
            if variable in self.data_from_csvs[file].columns:
                return file
        return None

    '''
        inputs:
        config: individual sections from the config file;
        st: start time in datetime
        et: end time in datetimpe
        
        returns df: each column is the timeseries of the variable in config['vm'] 
    '''
    def get_timeseries_from_config(self, config, st=None, et=None):
        # TODO: handle st, et for influx and XBOS versions
        # if st!=None and et!=None:
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

    '''
    inputs: 
    variable_list: list of variable names
    st: start time in datetime
    et: end time in datetime
    
    returns df: each column is the timeseries of the variable in the variable_list
    '''
    def get_data(self, variable_list, st=None, et=None):
        # TODO: handle st, et for influx and XBOS versions
        # if st!=None and et!=None:
        #     # get data for that time period

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


    '''
        This function takes in the dataframe from control_config and processes it to add more columns relevant to MPCPy
        input:
        df: columns=['FreComp', 'RefComp', 'HVAC1']
        
        output:
        df: columns=['FreComp', 'RefComp', 'HVAC1', 'Defrost', 'FreComp_Split',
                    'FreHeater_Split', 'FreComp_Split_Norm', 'FreHeater_Split_Norm',
                    'RefComp_Norm', 'HVAC1_Norm', 'uHeat', 'uCharge', 'uDischarge']
    '''
    def modify_control_df(self, df_power, pre_fix=False):
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

    '''
    inputs:
    config: individual config section (required keys are path, vm and type)
    st: start time in datetime
    et: end time in datetime
    
    outputs:
    df: each column is the timeseries of the variable in config['vm']
    '''
    def get_data_from_config(self, config, st=None, et=None):
        df = self.get_timeseries_from_config(config=config, st=st, et=et)
        if config['path'] == 'data/Control2.csv':
            return self.modify_control_df(df_power=df)
        return df
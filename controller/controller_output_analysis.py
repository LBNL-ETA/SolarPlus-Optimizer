#!/usr/bin/env python
# coding: utf-8

# ## This notebook is to analyze the output results of MPCPy for the Solar+ project

import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
from itertools import cycle

# ### Measured meter power
filepath = os.path.dirname(os.path.abspath(__file__))
meter_file = 'validation/meter_readings_20190917T1155.csv'
meter = pd.read_csv(os.path.join(filepath,meter_file),index_col=0)
meter.index = pd.to_datetime(meter.index,utc=True)
meter = meter.tz_convert('America/Los_Angeles')
sample_rate = '15T'
meter = meter.resample(sample_rate).mean()

# ### PG&E billing data
bill_file_201908 = 'validation/PlayStation777 IntervalData Jun-Sep2019/Historical_20190801-20190831.csv'
bill_file_201909 = 'validation/PlayStation777 IntervalData Jun-Sep2019/Historical_20190901-20190923.csv'
bill_201908 = pd.read_csv(os.path.join(filepath,bill_file_201908),index_col='Time')
bill_201909 = pd.read_csv(os.path.join(filepath,bill_file_201909),index_col='Time')
# remove the duplicated second half of the data with usage value=0
bill_201908 = bill_201908[0:len(bill_201908)/2]
bill_201909 = bill_201909[0:len(bill_201909)/2]
# combine two dataframes
bill = pd.concat([bill_201908, bill_201909])
bill.index = pd.to_datetime(bill.index).tz_localize('America/Los_Angeles')

bill_power = bill['Usage Value']/15*60
start_meter = bill_power.index[0]
end_meter = bill_power.index[-1]

meter_power = meter['building_main_Demand']/1000
plt.figure()
plt.rcParams["figure.figsize"] = [20,6]
plt.rcParams.update({'font.size': 16})
bill_power.loc[start_meter:end_meter].plot(label='bill')
meter_power.plot(label='meter')
plt.legend()
plt.ylabel('Power [kW]');

delta_P = bill_power.loc[start_meter:end_meter] - meter_power
delta_P.plot(label='Absolute power difference [kW]')
plt.legend()
plt.figure()
delta_per = (bill_power.loc[start_meter:end_meter] - meter_power)/meter_power*100
delta_per.plot(label='Relative difference [%]')
plt.legend()
# plt.show()

# ### Print optimization statistics

run_period = '2020-01'
outpath = os.path.join(filepath,'output')
plt.rcParams.update({'font.size': 16})
opt_stats = []
for i in os.listdir(outpath):
    file = os.path.join(outpath,i)
    if os.path.isfile(file) and 'optimal_statistics_'+run_period in i:
        with open(file) as files:
            lineList = files.readlines()
            if len(lineList) > 0:
                opt_stats.append(lineList[-1].split(', '))

opt_stats = pd.DataFrame(opt_stats)
columns = ['Datetime','iterative nb','cost function','runtime']
opt_stats.columns = columns
opt_stats['Time'] = opt_stats['Datetime'].str.split('(').str[0].str.split(': ').str[0]
opt_stats.index = pd.to_datetime(opt_stats['Time'])
opt_stats['runtime'] = opt_stats['runtime'].str.split(')').str[0].astype(dtype=np.float64)/60
opt_stats['iterative nb'] = opt_stats['iterative nb'].astype(dtype=np.float64)
opt_stats['solution'] = opt_stats['Datetime'].str.split(': ').str[1].str.split('(').str[1]
opt_stats.drop(['Datetime'], axis=1, inplace=True)
opt_stats.sort_values(by=['Time'], inplace=True)
plt.figure(1)
opt_stats['runtime'].plot(figsize=(16,4),title='Runtime')
plt.ylabel('Time [min]')
plt.figure(2)
opt_stats['iterative nb'].plot(figsize=(16,4),title='Iteration number')

pd.set_option('display.max_rows', 1003)
print(opt_stats)

# ### Measured temperatures
thermostat_file = 'validation/thermostat_readings_20190917T1155.csv'
thermostat = pd.read_csv(os.path.join(filepath,thermostat_file),index_col=0)
thermostat.index = pd.to_datetime(thermostat.index)
thermostat = thermostat.resample(sample_rate).mean()
start_time = '2019-09-01 00:00:00'
thermostat_range = thermostat.loc[start_time:]

parker_file = 'validation/parker_controller_readings_20190917T1155.csv'
parker = pd.read_csv(os.path.join(filepath, parker_file),index_col=0)
parker.index = pd.to_datetime(parker.index)
parker_range = parker.loc[start_time:]

plt.rcParams["figure.figsize"] = [16,4]
#thermostat_range['thermostat_west_space_temp'].plot(legend=True)
#thermostat_range['thermostat_east_space_temp'].plot(legend=True);
thermostat_range.head(10)


# ### Predicted temperatures

plt.rcParams["figure.figsize"] = [20,4]
plt.rcParams.update({'font.size': 16})
run_period = '2019-10-07'
for i in os.listdir(filepath):
    file = os.path.join(filepath,i)
    if os.path.isfile(file) and 'measurements_'+run_period in i:
        df = pd.read_csv(file, index_col='Time')
        df.index = pd.to_datetime(df.index)
        df = df.resample('15T').mean()
        plt.figure(1)
        for column in df.columns:
            if column == 'Trtu':
                HVAC = (df[column]-273.15)*9/5+32
                plt.plot(df[column].index, HVAC, linestyle='solid')
                plt.title('HVAC west temperature')
                plt.ylabel('$\degree$F')
                # plt.ylim([72.5,76.5])
                #thermostat_range['thermostat_west_space_temp'].plot(linestyle='dotted')
                plt.grid(linestyle='dotted')

        plt.figure(2)
        for column in df.columns:
            if column == 'Tref':
                Ref = (df[column]-273.15)*9/5+32
                plt.plot(df[column].index, Ref, linestyle='solid')
                plt.title('Refrigerator temperature')
                plt.ylabel('$\degree$F')
                plt.grid(linestyle='--')

        plt.figure(3)
        for column in df.columns:
            if column == 'Tfre':
                Fre = (df[column]-273.15)*9/5+32
                plt.plot(df[column].index, Fre, linestyle='solid')
                plt.title('Freezer temperature')
                plt.ylabel('$\degree$F')
                plt.grid(linestyle='--')

        plt.figure(4)
        for column in df.columns:
            if column == 'SOC':
                #Fre = (df[column]-273.15)*9/5+32
                plt.plot(df[column].index, df[column], linestyle='solid')
                plt.title('SOC')
                #plt.ylabel('$\degree$F')
                plt.grid(linestyle='--')


# ### Predicted HVAC power

plt.rcParams["figure.figsize"] = [16,4]
plt.rcParams.update({'font.size': 16})
simulation = pd.DataFrame()
for i in os.listdir(filepath):
    file = os.path.join(filepath,i)
    if os.path.isfile(file) and 'other_outputs_'+run_period in i:
        df = pd.read_csv(file, index_col='Time')
        df.index = pd.to_datetime(df.index)
        df = df.resample('5T').mean()
        plt.figure(1)
        for column in df.columns:
            if column == 'Prtu':
                plt.plot(df[column].index, df[column])
                plt.title('HVAC power')
                plt.ylabel('W')
                # meter_range['hvac_west_comp_Demand'].plot()
                plt.grid(linestyle='--')


# ### Plot predicted control trajectory

plt.rcParams["figure.figsize"] = [16,4]
plt.rcParams.update({'font.size': 16})
for i in os.listdir(filepath):
    file = os.path.join(filepath,i)
    run_period = '2019-10-07'
    if os.path.isfile(file) and 'control_'+run_period in i:
        df = pd.read_csv(file, index_col='Time')
        df.index = pd.to_datetime(df.index)
        df.index = df.index.tz_localize('America/Los_Angeles')
        df = df.resample('15T').mean()
        # df.index = df.index.astype(str).str[:-6]
        plt.figure(1)
        for column in df.columns:
            if column == 'uCool':
                plt.plot(df.index, df[column], linestyle='solid')
                plt.title('cooling control')
                #thermostat_range['thermostat_west_space_temp'].plot(linestyle='dotted')
                plt.grid(linestyle='dotted')

        plt.figure(2)
        for column in df.columns:
            if column == 'uHeat':
                plt.plot(df.index, df[column], linestyle='solid')
                plt.title('heating control')
                #thermostat_range['thermostat_west_space_temp'].plot(linestyle='dotted')
                plt.grid(linestyle='dotted')

        plt.figure(3)
        for column in df.columns:
            if column == 'uRef':
                plt.plot(df.index, df[column], linestyle='solid')
                # plt.title('Refrigerator control')
                plt.title('Normalized refrigerator power')
                #thermostat_range['thermostat_west_space_temp'].plot(linestyle='dotted')
                plt.grid(linestyle='dotted')

        plt.figure(4)
        for column in df.columns:
            if column == 'uFreCool':
                plt.plot(df.index, df[column], linestyle='solid')
                #plt.title('Freezer control')
                plt.title('Normalized freezer power')
                #thermostat_range['thermostat_west_space_temp'].plot(linestyle='dotted')
                plt.grid(linestyle='dotted')


        plt.figure(5)
        for column in df.columns:
            if column == 'uBattery':
                plt.plot(df.index, df[column], linestyle='solid')
                #plt.title('Battery control')
                plt.title('Normalized battery power')
                #thermostat_range['thermostat_west_space_temp'].plot(linestyle='dotted')
                plt.grid(linestyle='dotted')


# ### Plot other outputs

plt.rcParams["figure.figsize"] = [16,4]
plt.rcParams.update({'font.size': 16})
for i in os.listdir(filepath):
    file = os.path.join(filepath,i)
    run_period = '2019-10-07'
    if os.path.isfile(file) and 'other_outputs_'+run_period in i:
        df = pd.read_csv(file, index_col='Time')
        df.index = pd.to_datetime(df.index)
        df = df.resample('15T').mean()
        plt.figure(1)
        for column in df.columns:
            if column == 'Pnet':
                plt.plot(df[column])
                plt.title(column)
                plt.grid(linestyle='--')
        plt.figure(2)
        for column in df.columns:
            if column == 'Prtu':
                df[column].plot()
                plt.title('RTU cooling power [W]')
                plt.grid(linestyle='--')
        plt.figure(3)
        for column in df.columns:
            if column == 'Pbattery':
                plt.plot(df[column])
                plt.title(column + ' [W]')
                plt.grid(linestyle='--')
        plt.figure(4)
        for column in df.columns:
            if column == 'Pfre':
                plt.plot(df[column])
                plt.title(column + ' [W]')
                plt.grid(linestyle='--')
        plt.figure(5)
        for column in df.columns:
            if column == 'Pref':
                plt.plot(df[column])
                plt.title(column + ' [W]')
                plt.grid(linestyle='--')
        plt.figure(6)
        for column in df.columns:
            if column == 'Grtu':
                df[column].plot()
                plt.title('RTU heating power [W]')
                plt.grid(linestyle='--')
        plt.figure(7)
        for column in df.columns:
            if column == 'Ppv':
                df[column].plot()
                plt.title('PV power [W]')
                plt.grid(linestyle='--')

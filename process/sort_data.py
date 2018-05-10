# -*- coding: utf-8 -*-
"""
This script sorts the downloaded csv data into a more useable format.
"""

import pandas as pd
import os
from matplotlib import pyplot as plt

def Temperature():
    # Temperature Data
    directory = os.path.join('data', 'Raw_Data_Temperature')
    csvs = os.listdir(directory)
    df = pd.DataFrame()
    for csv in csvs:
        filepath = os.path.join('data', 'Raw_Data_Temperature', csv)
        df_file = pd.read_csv(filepath)
        df_file = df_file.pivot(index='Timestamp', columns='Sensor Name', values='Temperature ( C )')
        # Append data for each csv file to dataframe
        df = df.append(df_file)
    df.index = pd.to_datetime(df.index)
    df.index.name = 'Time'
    df.sort_index(inplace=True)
    df.to_csv(os.path.join('data','Temperature.csv'))
    df.plot()
    plt.show()

def Power():
    # Power Data
    columns = {'Total.Real.Power.1':'RefEvapFans',
               'Total.Real.Power.2':'RefComp',
               'Total.Real.Power.3':'FreComp',
               'Total.Real.Power.4':'Building',
               'Total.Real.Power.5':'HVAC1',
               'Total.Real.Power.6':'HVAC2'}
    # Locate files
    directory = os.path.join('data','Cleaned_Daily_Data','Power')
    csvs = os.listdir(directory)
    # Initialize dataframe
    df = pd.DataFrame()
    # For each csv file
    for csv in csvs:
        print(csv)
        # Read data into dataframe
        filepath = os.path.join(directory,csv)
        df_file = pd.read_csv(filepath, index_col='Time.of.Day', usecols=columns.keys()+['Time.of.Day'])
        # Replace index
        day = csv[:-10]
        index = []
        for value in df_file.index.values:
            time = str(value)
            datetime = pd.to_datetime('{0} {1}'.format(day, time))
            index.append(datetime)
        df_file.index = index
        # Replace columns
        df_file.rename(columns=columns, inplace=True)
        # Append data for each csv file to dataframe
        df = df.append(df_file)
    # Process dataframe  
    df.index.name = 'Time'
    print('Sorting index...')
    df.sort_index(inplace=True)
    print('Writing csv...')
    df.to_csv(os.path.join('data','Power.csv'))
    
def HistoricMicrogrid():
    # Historic Microgrid Data
    directory = os.path.join('data', 'Historiac_microgrid_data')
    # Collect csvs except raw data
    csvs = os.listdir(directory)
    for csv in csvs:
        if ('raw' in csv) or ('docx' in csv):
            csvs.remove(csv)
    for i,csv in enumerate(csvs):
        filepath = os.path.join(directory, csv)
        df_file = pd.read_csv(filepath, index_col='Date_PT')
        # Append data for each csv file to dataframe
        if i == 0:
            df = df_file
        else:
            df = df.join(df_file)
    df.index = pd.to_datetime(df.index)
    df.index.name = 'Time'
    df.sort_index(inplace=True)
    df.to_csv(os.path.join('data','HistoricMicrogrid.csv'))

HistoricMicrogrid()
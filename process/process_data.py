# -*- coding: utf-8 -*-
"""
This script processes data to make calculations or view.

"""

import pandas as pd
from matplotlib import pyplot as plt
import os
import numpy as np

# microgrid headers
# PVPower_kW	
# BatteryStateOfCharge_Percent	
# RelativeHumidity_Percent	
# AirTemp_degC	
# BatteryPower_kW	
# PlaneArrayIrradiance_W/m2

# What is efficiency from POA irradiation?
def pv_eff():
    '''Calculates the efficiency of the PV panels.'''
    
    # Read data
    csvpath = os.path.join('data','HistoricMicrogrid.csv')
    PV_area = (156.75e-3*156.75e-3)*72*1548 #72 cells/module, 1548 modules
    df = pd.read_csv(csvpath, index_col = 'Time')
    df.index = pd.to_datetime(df.index.values)
    df = df.where(df['PVPower_kW']>0).dropna()
    df['PVEff'] = df['PVPower_kW']/(df['PlaneArrayIrradiance_W/m2']/1000*PV_area)
    # Regress
    x = df['PVPower_kW'].where((df['PVPower_kW']>=100) & (df['PVEff']>=0.14)).dropna().get_values()
    y = df['PVEff'].where((df['PVPower_kW']>=100) & (df['PVEff']>=0.14)).dropna().get_values()
    coeffs = np.polyfit(x,y,1)
    p = np.poly1d(coeffs)
    # Plot
    plt.figure(1)    
    df['PVEff'].plot()
    plt.ylim([0,0.5])

    plt.figure(2)
    plt.plot(df['PlaneArrayIrradiance_W/m2'],df['PVEff'], 'ob', alpha = 0.2)
    plt.ylim([0,0.5])
    plt.title('Eff vs. POA')
    
    plt.figure(3)
    model = p(df['PVPower_kW'])
    plt.plot(df['PVPower_kW'],df['PVEff'], 'og', alpha = 0.2)
    plt.plot(df['PVPower_kW'],model, '-k', linewidth = 3.0)
    plt.ylim([0,0.5])
    plt.title('Eff vs. Power Gen')
    
    plt.figure(4)
    plt.plot(df['AirTemp_degC'],df['PVEff'], 'or', alpha = 0.2)
    plt.ylim([0,0.5])
    plt.title('Eff vs. OAT')
    
    plt.show()

# What is the battery charging and discharging efficiency?

# How good are models to calculate POA irradiation?
def poa_test():
    # Get poa from historic data
    csvpath = os.path.join('data','HistoricMicrogrid.csv')
    poa = df['PlaneArrayIrradiance_W/m2']
    # Get glob hor from weather underground KCABLUEL2
    
def ref_operation(start_time, final_time):
    start_time = pd.to_datetime(start_time)
    final_time = pd.to_datetime(final_time)
    # Get temperature from historic data
    csvpath = os.path.join('data','Temperature.csv')
    df_temp = pd.read_csv(csvpath, index_col = 'Time')
    df_temp.index = pd.to_datetime(df_temp.index.values)
    # Get power from historic data
    csvpath = os.path.join('data','Power.csv')
    df_power = pd.read_csv(csvpath, index_col = 'Time')
    df_power.index = pd.to_datetime(df_power.index.values)
    # Bin power
    df_power_bin = df_power.resample('60T').mean()
    df_power_bin = df_power_bin.resample('1T').fillna('pad')
    
    fix,ax = plt.subplots(3,1, sharex=True)
    ax[0].plot(df_temp['Refrigerator East'].loc[start_time:final_time], label='East', alpha=0.75)
    ax[0].plot(df_temp['Refrigerator West'].loc[start_time:final_time], label='West', alpha=0.75)
    ax[0].legend()
    ax[1].plot(df_power['RefComp'].loc[start_time:final_time], label='Compressor')
    ax[1].plot(df_power['RefEvapFans'].loc[start_time:final_time], label='Fans')
    ax[1].legend()
    ax[2].plot(df_power_bin['RefComp'].loc[start_time:final_time], label='Binned Compressor')
    ax[2].plot(df_power_bin['RefEvapFans'].loc[start_time:final_time], label='Binned Fans')
    ax[2].legend()
    plt.show()
    
def fre_operation(start_time, final_time):
    start_time = pd.to_datetime(start_time)
    final_time = pd.to_datetime(final_time)
    # Get temperature from historic data
    csvpath = os.path.join('data','Temperature.csv')
    df_temp = pd.read_csv(csvpath, index_col = 'Time')
    df_temp.index = pd.to_datetime(df_temp.index.values)
    # Get power from historic data
    csvpath = os.path.join('data','Power.csv')
    df_power = pd.read_csv(csvpath, index_col = 'Time')
    df_power.index = pd.to_datetime(df_power.index.values)
    # Bin power
    df_power_bin = df_power.resample('60T').mean()
    df_power_bin = df_power_bin.resample('1T').fillna('pad')
    
    fix,ax = plt.subplots(3,1, sharex=True)
    ax[0].plot(df_temp['Freezer'].loc[start_time:final_time], label='Freezer')
    ax[0].legend()
    ax[1].plot(df_power['FreComp'].loc[start_time:final_time], label='Compressor')
    ax[1].legend()
    ax[2].plot(df_power_bin['FreComp'].loc[start_time:final_time], label='Binned Compressor')
    ax[2].legend()
    plt.show()
    
def HVAC_operation(start_time, final_time):
    start_time = pd.to_datetime(start_time)
    final_time = pd.to_datetime(final_time)
    # Get temperature from historic data
    csvpath = os.path.join('data','Temperature.csv')
    df_temp = pd.read_csv(csvpath, index_col = 'Time')
    df_temp.index = pd.to_datetime(df_temp.index.values)
    # Get power from historic data
    csvpath = os.path.join('data','Power.csv')
    df_power = pd.read_csv(csvpath, index_col = 'Time')
    df_power.index = pd.to_datetime(df_power.index.values)
    # Bin power
    df_power_bin = df_power.resample('60T').mean()
    df_power_bin = df_power_bin.resample('1T').fillna('pad')
    
    fix,ax = plt.subplots(3,1, sharex=True)
    ax[0].plot(df_temp['Break Area'].loc[start_time:final_time], label='Break Area', alpha=0.75)
    ax[0].plot(df_temp['Employee Area'].loc[start_time:final_time], label='Employee Area', alpha=0.75)
    ax[0].plot(df_temp['Crawlspace'].loc[start_time:final_time], label='Crawlspace', alpha=0.75)
    ax[0].plot(df_temp['HVAC East'].loc[start_time:final_time], label='HVAC East', alpha=0.75)
    ax[0].plot(df_temp['HVAC West'].loc[start_time:final_time], label='HVAC West', alpha=0.75)
    ax[0].plot(df_temp['Outdoor'].loc[start_time:final_time], label='Outdoor', alpha=0.75)
    ax[0].legend()
    ax[1].plot(df_power['HVAC1'].loc[start_time:final_time], label='HVAC 1')
    ax[1].plot(df_power['HVAC2'].loc[start_time:final_time], label='HVAC 2')
    ax[1].legend()
    ax[2].plot(df_power_bin['HVAC1'].loc[start_time:final_time], label='Binned HVAC 1')
    ax[2].plot(df_power_bin['HVAC2'].loc[start_time:final_time], label='Binned HVAC 2')
    ax[2].legend()
    plt.show()
    
def building_operation(start_time, final_time):
    start_time = pd.to_datetime(start_time)
    final_time = pd.to_datetime(final_time)
    # Get temperature from historic data
    csvpath = os.path.join('data','Temperature.csv')
    df_temp = pd.read_csv(csvpath, index_col = 'Time')
    df_temp.index = pd.to_datetime(df_temp.index.values)
    # Get power from historic data
    csvpath = os.path.join('data','Power.csv')
    df_power = pd.read_csv(csvpath, index_col = 'Time')
    df_power.index = pd.to_datetime(df_power.index.values)
    fix,ax = plt.subplots(6,1, sharex=True)
    ax[0].plot(df_power['Building'].loc[start_time:final_time], label='Building')
    ax[0].legend()
    ax[1].plot(df_power['HVAC1'].loc[start_time:final_time] + \
               df_power['HVAC2'].loc[start_time:final_time] + \
               df_power['RefComp'].loc[start_time:final_time] - \
               df_power['RefEvapFans'].loc[start_time:final_time] + \
               df_power['FreComp'].loc[start_time:final_time], label='Added')
    ax[1].legend()
    ax[2].plot(df_power['HVAC1'].loc[start_time:final_time], label='HVAC 1')
    ax[2].plot(df_power['HVAC2'].loc[start_time:final_time], label='HVAC 2')
    ax[2].legend()
    ax[3].plot(df_power['RefComp'].loc[start_time:final_time], label='Ref Comp')
    ax[3].plot(df_power['RefEvapFans'].loc[start_time:final_time], label='Ref Fans')
    ax[3].legend()
    ax[4].plot(df_power['FreComp'].loc[start_time:final_time], label='Fre Comp')
    ax[4].legend()    
    ax[5].plot(df_temp['Outdoor'].loc[start_time:final_time], label='Outdoor')
    ax[5].legend()
    plt.show()

def all_operation(start_time, final_time):    
    start_time = pd.to_datetime(start_time)
    final_time = pd.to_datetime(final_time)
    # Get temperature from historic data
    csvpath = os.path.join('data','Temperature.csv')
    df_temp = pd.read_csv(csvpath, index_col = 'Time')
    df_temp.index = pd.to_datetime(df_temp.index.values)
    # Get power from historic data
    csvpath = os.path.join('data','Power.csv')
    df_power = pd.read_csv(csvpath, index_col = 'Time')
    df_power.index = pd.to_datetime(df_power.index.values)
    
    fix,ax = plt.subplots(6,1, sharex=True)
    ax[0].plot(df_temp['Break Area'].loc[start_time:final_time], label='Break Area', alpha=0.75)
    ax[0].plot(df_temp['Employee Area'].loc[start_time:final_time], label='Employee Area', alpha=0.75)
    ax[0].plot(df_temp['Crawlspace'].loc[start_time:final_time], label='Crawlspace', alpha=0.75)
    ax[0].plot(df_temp['HVAC East'].loc[start_time:final_time], label='HVAC East', alpha=0.75)
    ax[0].plot(df_temp['HVAC West'].loc[start_time:final_time], label='HVAC West', alpha=0.75)
    ax[0].plot(df_temp['Outdoor'].loc[start_time:final_time], label='Outdoor', alpha=0.75)
    ax[0].legend()
    ax[1].plot(df_power['HVAC1'].loc[start_time:final_time], label='HVAC 1')
    ax[1].plot(df_power['HVAC2'].loc[start_time:final_time], label='HVAC 2')
    ax[1].legend()
    ax[2].plot(df_temp['Refrigerator East'].loc[start_time:final_time], label='Ref East', alpha=0.75)
    ax[2].plot(df_temp['Refrigerator West'].loc[start_time:final_time], label='Ref West', alpha=0.75)
    ax[2].legend()
    ax[3].plot(df_power['RefComp'].loc[start_time:final_time], label='Ref Comp')
    ax[3].plot(df_power['RefEvapFans'].loc[start_time:final_time], label='Ref Fans')
    ax[3].legend()
    ax[4].plot(df_temp['Freezer'].loc[start_time:final_time], label='Fre')
    ax[4].legend()
    ax[5].plot(df_power['FreComp'].loc[start_time:final_time], label='Fre Comp')
    ax[5].legend()
    plt.show()
        
    
    
    
HVAC_operation('4/8/2018 00:00:00', '4/10/2018 00:00:00')
    
    
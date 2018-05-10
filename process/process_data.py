# -*- coding: utf-8 -*-
"""
Created on Mon May  7 07:59:16 2018

@author: dhb-lx
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
    
    fix,ax = plt.subplots(2,1, sharex=True)
    ax[0].plot(df_temp['Refrigerator East'].loc[start_time:final_time], label='East')
    ax[0].plot(df_temp['Refrigerator West'].loc[start_time:final_time], label='West')
    ax[1].plot(df_power['RefComp'].loc[start_time:final_time], label='Compressor')
    ax[1].plot(df_power['RefEvapFans'].loc[start_time:final_time], label='Fans')
    plt.show()
        
    
    
    
ref_operation('3/24/2018 13:00:00', '3/24/2018 15:00:00')
    
    
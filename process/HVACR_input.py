# -*- coding: utf-8 -*-
"""
This script prepares HVACR input data for parameter estimation.
"""

import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
from itertools import cycle

meter = pd.read_csv('meter_readings_20191111T0942.csv',index_col=0)
meter.index = pd.to_datetime(meter.index)
start_time = '2019-11-06 08:00:00'
meter_range = meter.loc[start_time:]
sample_rate = '5T'
meter_range = meter_range.resample(sample_rate).mean()
# meter_range['hvac_east_comp_Demand'].plot(legend=True)
# meter_range['hvac_west_comp_Demand'].plot(legend=True)

# calculate equipment maximum capacity and internal load
ref_load = meter['ref_evapfan_Demand']+meter['ref_comp_Demand']
equip_load = ref_load+meter['fre_comp_evapfan_Demand']+meter['hvac_west_comp_Demand']+meter['hvac_east_comp_Demand']
internal_load = meter['building_main_Demand'] - equip_load
HVAC_west_cap = max(meter['hvac_west_comp_Demand'])
HVAC_east_cap = max(meter['hvac_east_comp_Demand'])
fre_cap = max(meter['fre_comp_evapfan_Demand'])
ref_cap = max(ref_load)
internal_load_cap = max(internal_load)
internal_load_ave = np.mean(internal_load)
print("HVAC west capacity is {} W".format(HVAC_west_cap))
print("HVAC east capacity is {} W".format(HVAC_east_cap))
print("Freezer capacity is {} W".format(fre_cap))
print("Refrigerator capacity is {} W".format(ref_cap))
print("Internal load max is {0} W and average is {1} W".format(internal_load_cap,internal_load_ave))

normalized_power = pd.DataFrame(index=range(5*24*12))
# HVAC west
HVAC_West_Norm = meter_range['hvac_west_comp_Demand']/HVAC_west_cap
HVAC_West = cycle(HVAC_West_Norm.tolist())
normalized_power['HVAC_West_Norm'] = [next(HVAC_West) for count in range(normalized_power.shape[0])]
# HVAC east
HVAC_East_Norm = meter_range['hvac_east_comp_Demand']/HVAC_east_cap
HVAC_East = cycle(HVAC_East_Norm.tolist())
normalized_power['HVAC_East_Norm'] = [next(HVAC_East) for count in range(normalized_power.shape[0])]
# Freezer
FreComp_Split_Norm = meter_range['fre_comp_evapfan_Demand']/fre_cap
fre = cycle(FreComp_Split_Norm.tolist())
normalized_power['FreComp_Split_Norm'] = [next(fre) for count in range(normalized_power.shape[0])]
# Refrigerator
RefComp_Norm = meter_range['ref_comp_Demand']/ref_cap
ref = cycle(RefComp_Norm.tolist())
normalized_power['RefComp_Norm'] = [next(ref) for count in range(normalized_power.shape[0])]
# heating and battery
normalized_power['uHeat'] = 0
normalized_power['uBattery'] = 0
normalized_power['uFreDef'] = 0
normalized_power.index = pd.date_range(start_time, '2019-11-11 07:55:00', freq=sample_rate, tz='UTC')
normalized_power.index.names = ['time']
normalized_power.to_csv('normalized_power_201911.csv')

thermostat = pd.read_csv('thermostat_readings_20191111T0942.csv',index_col=0,parse_dates=True)
thermostat.index = thermostat.index.tz_localize('UTC')
thermostat = thermostat.resample(sample_rate).mean()
thermostat_range = thermostat.loc[start_time:]

parker = pd.read_csv('parker_controller_readings_20191111T0942.csv',index_col=0,parse_dates=True)
parker.index = parker.index.tz_localize('UTC')
parker_range = parker.loc[start_time:]

# output temperatures for model calibration
temperature = pd.DataFrame(index=thermostat_range.index)
temperature['temp_rtu_east_k'] = (thermostat_range['thermostat_east_space_temp']-32)/1.8+273.15
temperature['temp_rtu_west_k'] = (thermostat_range['thermostat_west_space_temp']-32)/1.8+273.15
temperature['ref_k'] = (parker_range['refrigerator_CabinetTemperature']-32)/1.8+273.15
temperature['fre_k'] = (parker_range['freezer_CabinetTemperature']-32)/1.8+273.15
temperature.index.names = ['time']
temperature.to_csv('temperature_201911.csv')

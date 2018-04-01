# -*- coding: utf-8 -*-
'''
This script demonstrates solving the optimal control problem for the store.

'''

from mpcpy import units, variables, exodata, models, optimization
import pandas as pd
import os
from matplotlib import pyplot as plt

# Setup
# --------------------------------------------------------------------------
# MPC operating periods
start_time = '6/1/2017 00:00:00'
final_time = '6/2/2017 00:00:00'
# Weather data
epwpath = 'models/weatherdata/DRYCOLDTMY.epw'
# Model definition
mopath = 'models/MPC/package.mo'
modelpath = 'MPC.Building.Whole'
# Model measurements
meas_list = ['Tzone', 'SOC', 'Ppv', 'Pheat', 'Pcool', 'Pcharge', 'Pdischarge', 'Pnet']
sample_rate = 3600;
# Optimization objective
objective = 'EnergyMin'
# Optimization constraints (adjustable)
Tzone_max = 25.0
Tzone_min = 20.0
SOC_max = 1.0
SOC_min = 0.25
# Price signal
peak_start = 14
peak_end = 17
multiplier = 10
# --------------------------------------------------------------------------

# Initialize
# --------------------------------------------------------------------------

# Exodata
# --------------------------------------------------------------------------
# Instantiate weather object
weather = exodata.WeatherFromEPW(epwpath);
# Collect weather data
weather.collect_data(start_time, final_time);
# --------------------------------------------------------------------------

# Measurements
# --------------------------------------------------------------------------
# Build measurements dictionary
measurements = dict()
for meas in meas_list:
    measurements[meas] = {'Sample' : variables.Static('{0}_sample'.format(meas), sample_rate, units.s)};
# --------------------------------------------------------------------------

# Controls
# --------------------------------------------------------------------------
# Build dataframe
time = pd.to_datetime(start_time)
controls_df = pd.DataFrame(index=[time])
controls_df.index.name = 'Time'
controls_df.loc[time,'uHeat'] = 0.01
controls_df.loc[time,'uCool'] = 0.01
controls_df.loc[time,'uCharge'] = 0.01
controls_df.loc[time,'uDischarge'] = 0.01
# Define variable map
vm_controls = {'uHeat'      : ('uHeat',      units.unit1),
               'uCool'      : ('uCool',      units.unit1),
               'uCharge'    : ('uCharge',    units.unit1),
               'uDischarge' : ('uDischarge', units.unit1)}
# Instantiate object                  
controls = exodata.ControlFromDF(controls_df, 
                                 vm_controls, 
                                 tz_name = weather.tz_name);
# Collect data
controls.collect_data(start_time, final_time)
# --------------------------------------------------------------------------

# Constraints
# --------------------------------------------------------------------------
# Build dataframe
time = pd.to_datetime(start_time)
constraints_df = pd.DataFrame(index=[time])
constraints_df.index.name = 'Time'
constraints_df.loc[time,'Tzone_max'] = Tzone_max
constraints_df.loc[time,'Tzone_min'] = Tzone_min
constraints_df.loc[time,'SOC_max'] = SOC_max
constraints_df.loc[time,'SOC_min'] = SOC_min
constraints_df.loc[time,'uHeat_max'] = 1.0
constraints_df.loc[time,'uHeat_min'] = 0.0
constraints_df.loc[time,'uCool_max'] = 1.0
constraints_df.loc[time,'uCool_min'] = 0.0
# Define variable map
vm_constraints = {'Tzone_max' : ('Tzone', 'LTE', units.degC),
                  'Tzone_min' : ('Tzone', 'GTE', units.degC),
                  'SOC_max'   : ('SOC',   'LTE', units.unit1),
                  'SOC_min'   : ('SOC',   'GTE', units.unit1),
                  'uHeat_max' : ('uHeat', 'LTE', units.unit1),
                  'uHeat_min' : ('uHeat', 'GTE', units.unit1),
                  'uCool_max' : ('uCool', 'LTE', units.unit1),
                  'uCool_min' : ('uCool', 'GTE', units.unit1)}
# Instantiate object                  
constraints = exodata.ConstraintFromDF(constraints_df, 
                                       vm_constraints, 
                                       tz_name = weather.tz_name);
# Collect data
constraints.collect_data(start_time, final_time)
# --------------------------------------------------------------------------

# Prices
# --------------------------------------------------------------------------
# Build dataframe
time = pd.date_range(start_time, final_time, freq='5T')
prices_df = pd.DataFrame(index=time)
for t in time:
    if (t.hour < peak_start) or (t.hour > peak_end):
        prices_df.loc[t,'energy_price'] = 1
    else:
        prices_df.loc[t,'energy_price'] = multiplier

# Define variable map
vm_prices = {'energy_price' : ('pi_e', units.dol_kWh)}
# Instantiate object                  
prices = exodata.PriceFromDF(prices_df, 
                               vm_prices, 
                               tz_name = weather.tz_name);
# Collect data
prices.collect_data(start_time, final_time)

# Model
# --------------------------------------------------------------------------
# Define model information
libraries = os.getenv('MODELICAPATH')
moinfo = (mopath, modelpath, libraries)
# Instantiate object
model = models.Modelica(models.JModelica,
                        models.RMSE,
                        measurements,
                        moinfo = moinfo,
                        weather_data = weather.data,
                        control_data = controls.data,
                        tz_name = weather.tz_name)
# --------------------------------------------------------------------------

# Optimization Problem
# --------------------------------------------------------------------------
# Define problem
if objective is 'EnergyMin':
    problem = optimization.EnergyMin
elif objective is 'EnergyCostMin':
    problem = optimization.EnergyCostMin
else:
    raise ValueError('Objective "{0}" unknown or not available.'.format(objective))
# Instantiate object
opt_problem = optimization.Optimization(model,
                                        problem,
                                        optimization.JModelica,
                                        'Pnet',
                                        constraint_data = constraints.data,
                                        tz_name = weather.tz_name)
# Set options
opt_options = opt_problem.get_optimization_options()
opt_options['n_e'] = 24
opt_problem.set_optimization_options(opt_options)
# --------------------------------------------------------------------------

# Solve
# --------------------------------------------------------------------------
# Solve optimization problem
if objective is 'EnergyMin':
    opt_problem.optimize(start_time, final_time, res_control_step=sample_rate)
elif objective is 'EnergyCostMin':
    opt_problem.optimize(start_time, final_time, price_data=prices.data, res_control_step=sample_rate)
else:
    raise ValueError('Objective "{0}" unknown or not available.'.format(objective))
opt_statistics = opt_problem.get_optimization_statistics()

# --------------------------------------------------------------------------

# Post Process
# --------------------------------------------------------------------------
# Plot
fig, ax = plt.subplots(4,1,sharex=True)
meas_opt = opt_problem.display_measurements('Simulated')
ax[0].plot(meas_opt['Tzone']-273.15, label='Tzone', color='r')
ax[0].set_title('Zone Temperature [degC]')
ax[0].set_ylim([18,28])
ax[1].plot(meas_opt['SOC'], label='SOC', color='g')
ax[1].set_title('Battery SOC [1]')
ax[1].set_ylim([0,1.25])
for meas in ['Pnet', 'Pheat', 'Pcool', 'Ppv', 'Pcharge', 'Pdischarge']:
    ax[2].plot(meas_opt[meas], label=meas)
ax[2].legend()
ax[2].set_title('Power [W]')
ax[2].set_ylim([-2500,2500])
ax[3].plot(prices.display_data(),label='Energy Price')
ax[3].set_title('Electricity Price [$/kWh]')
ax[3].set_ylim([0,15])
plt.savefig('process/results/optimal_{0}.png'.format(objective))
plt.show()

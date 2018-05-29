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
modelpath = 'MPC.Building.Whole_Derivative'
# Model measurements
meas_list = ['Tzone', 'SOC', 
             'Ppv', 'Pheat', 'Pcool', 'Pcharge', 'Pdischarge', 'Pnet', 
             'uCharge', 'uDischarge', 'uHeat', 'uCool', 
             'duCharge', 'duDischarge', 'duHeat', 'duCool']
sample_rate = 3600;
# Optimization objective
objective = 'EnergyCostMin'
# Optimization constraints
Tzone_max = 25.0
Tzone_min = 20.0
SOC_max = 1.0
SOC_min = 0.25
P_demand_limit = 1500
# Price signal
build_price = True
peak_start = 14
peak_end = 17
multiplier = 10
price_vec = [1,1,1.5,2,3,3.5,4,5,5.5,6,7,9,11,20,20,20,11,9,7,5.5,4,2.5,1.5,1,1] # if not build
# Initial states (must satisfy optimization constraints)
Tzone_0 = 22 # deg C
SOC_0 = 0.26 # unit 1
uHeat_0 = 0.01 # unit 1
uCool_0 = 0.01 # unit 1
uCharge_0 = 0.01 # unit 1
uDischarge_0 = 0.01 # unit 1

# --------------------------------------------------------------------------

# Exodata
# --------------------------------------------------------------------------
# Instantiate weather object
weather = exodata.WeatherFromEPW(epwpath);
# Collect weather data
weather.collect_data(start_time, final_time);
# Create parameter df
pars = {'Name':      ['Tzone_0', 'SOC_0', 'uHeat_0', 'uCool_0', 'uCharge_0', 'uDischarge_0'], 
        'Free':      [False,     False,   False,     False,     False,       False],
        'Value':     [Tzone_0,   SOC_0,   uHeat_0,   uCool_0,   uCharge_0,   uDischarge_0],
        'Minimum':   [0,         0,       0,         0,         0,           0],
        'Maximum':   [350,       1,       1,         1,         1,           1],
        'Covariance':[0,         0,       0,         0,         0,           0],
        'Unit' :     ['degC',   '1',      '1',       '1',       '1',         '1']}
par_df = pd.DataFrame(pars).set_index('Name')
# Instantiate parameter object
parameters = exodata.ParameterFromDF(par_df)
# Collect parameters
parameters.collect_data()
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
controls_df.loc[time,'duHeat'] = 0.00
controls_df.loc[time,'duCool'] = 0.00
controls_df.loc[time,'duCharge'] = 0.00
controls_df.loc[time,'duDischarge'] = 0.00
# Define variable map
vm_controls = {'duHeat'      : ('duHeat',      units.unit1),
               'duCool'      : ('duCool',      units.unit1),
               'duCharge'    : ('duCharge',    units.unit1),
               'duDischarge' : ('duDischarge', units.unit1)}
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
constraints_df.loc[time,'uCharge_max'] = 1.0
constraints_df.loc[time,'uCharge_min'] = 0.0
constraints_df.loc[time,'uDischarge_max'] = 1.0
constraints_df.loc[time,'uDischarge_min'] = 0.0
constraints_df.loc[time,'duHeat_max'] = 0.001
constraints_df.loc[time,'duHeat_min'] = -0.001
constraints_df.loc[time,'duCharge_max'] = 0.0005
constraints_df.loc[time,'duCharge_min'] = -0.0005
constraints_df.loc[time,'Pnet_max'] = P_demand_limit
# Define variable map
vm_constraints = {'Tzone_max' : ('Tzone', 'LTE', units.degC),
                  'Tzone_min' : ('Tzone', 'GTE', units.degC),
                  'SOC_max'   : ('SOC',   'LTE', units.unit1),
                  'SOC_min'   : ('SOC',   'GTE', units.unit1),
                  'uHeat_max' : ('uHeat', 'LTE', units.unit1),
                  'uHeat_min' : ('uHeat', 'GTE', units.unit1),
                  'uCool_max' : ('uCool', 'LTE', units.unit1),
                  'uCool_min' : ('uCool', 'GTE', units.unit1),
                  'uCharge_max' : ('uCharge', 'LTE', units.unit1),
                  'uCharge_min' : ('uCharge', 'GTE', units.unit1),
                  'uDischarge_max' : ('uCharge', 'LTE', units.unit1),
                  'uDischarge_min' : ('uCharge', 'GTE', units.unit1),
                  'duHeat_max' : ('duHeat', 'LTE', units.unit1),
                  'duHeat_min' : ('duHeat', 'GTE', units.unit1),
                  'duCharge_max' : ('duCharge', 'LTE', units.unit1),
                  'duCharge_min' : ('duCharge', 'GTE', units.unit1),
                  'Pnet_max' : ('Pnet', 'LTE', units.W),}
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
if build_price:
    time = pd.date_range(start_time, final_time, freq='5T')
    prices_df = pd.DataFrame(index=time)
    for t in time:
        if (t.hour < peak_start) or (t.hour > peak_end):
            prices_df.loc[t,'energy_price'] = 1
        else:
            prices_df.loc[t,'energy_price'] = multiplier
else:
    time = pd.date_range(start_time, final_time, freq='H')
    prices_df = pd.DataFrame(index=time, data=price_vec,columns=['energy_price'])

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
                        parameter_data = parameters.data,
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
opt_options['n_e'] = 24*4
opt_options['n_cp'] = 3
opt_options['IPOPT_options']['tol'] = 1e-10
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
fig, ax = plt.subplots(6,1,sharex=True)
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
for meas in ['uCharge', 'uDischarge']:
    ax[4].plot(meas_opt[meas], label=meas)
ax[4].legend()
ax[4].set_title('Signal [-]')
for meas in ['duCharge', 'duDischarge']:
    ax[5].plot(meas_opt[meas], label=meas)
ax[5].legend()
ax[5].set_title('Derivative Signal [-]')
plt.savefig('process/results/optimal_{0}.png'.format(objective))
plt.show()
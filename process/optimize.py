# -*- coding: utf-8 -*-
'''
This script demonstrates solving the optimal control problem for the store.

'''

from mpcpy import units, variables, exodata, models, optimization
import pandas as pd
import os
from matplotlib import pyplot as plt
from modules.costcalculator.tariff_solarplus import SolarPlusCombinedCostCalculator, TariffType

# Setup
# --------------------------------------------------------------------------
# MPC operating periods
start_time = '06/12/2017 00:00:00'
final_time = '06/13/2017 00:00:00'
# Weather data
epwpath = 'models/weatherdata/USA_CA_San.Francisco.Intl.AP.724940_TMY3.epw'
# Model definition
mopath = 'models/SolarPlus.mo'
modelpath = 'SolarPlus.Building.Whole_Inputs'
# Model measurements
meas_list = ['Trtu', 'Tref', 'Tfre', 'weaTDryBul', 'SOC', 
             'Prtu', 'Pref', 'Pfre', 'Pcharge', 'Pdischarge', 'Pnet', 'Ppv',
             'uCharge', 'uDischarge', 'uHeat', 'uCool', 'uRef', 'uFreCool']
sample_rate = 3600;
# Optimization objective
objective = 'EnergyCostMin'
# Optimization constraints
Trtu_max = 23.0
Trtu_min = 20.0
Tref_max = 5.0
Tref_min = 3.0
Tfre_max = -23.0
Tfre_min = -25.0
SOC_max = 1.0
SOC_min = 0.25
P_demand_limit = 100000
# Price signal
read_pge_tariff = True  # if True, use PGE tariff, else the custom vector below
build_price = True  # if False, use price_vec
peak_start = 14
peak_end = 17
multiplier = 3
price_vec = [1,1,1.5,2,3,3.5,4,5,5.5,6,7,9,11,20,20,20,11,9,7,5.5,4,2.5,1.5,1,1] # if not build
# Initial states (must satisfy optimization constraints)
Trtu_0 = 22 # deg C
Tref_0 = 4 # deg C
Tfre_0 = -23 # deg C
SOC_0 = 0.75 # unit 1

# --------------------------------------------------------------------------

# Exodata
# --------------------------------------------------------------------------
# Instantiate weather object
weather = exodata.WeatherFromEPW(epwpath);
# Collect weather data
weather.collect_data(start_time, final_time);
# Create parameter df
pars = {'Name':      ['Trtu_0', 'Tref_0', 'Tfre_0', 'SOC_0'], 
        'Free':      [False,    False,    False,    False],
        'Value':     [Trtu_0,   Tref_0,   Tfre_0,   SOC_0],
        'Minimum':   [10,       0,        -40,      0],
        'Maximum':   [35,       20,       0,        1],
        'Covariance':[0,        0,        0,        0],
        'Unit' :     ['degC',   'degC',   'degC',   '1']}
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
controls_df.loc[time,'uHeat'] = 0.5
controls_df.loc[time,'uCool'] = 0.5
controls_df.loc[time,'uRef'] = 0.5
controls_df.loc[time,'uFreCool'] = 0.5
controls_df.loc[time,'uCharge'] = 0.01
controls_df.loc[time,'uDischarge'] = 0.01
# Define variable map
vm_controls = {'uHeat'      : ('uHeat',      units.unit1),
               'uCool'      : ('uCool',      units.unit1),
               'uRef'       : ('uRef',       units.unit1),
               'uFreCool'   : ('uFreCool',   units.unit1),
               'uCharge'    : ('uCharge',    units.unit1),
               'uDischarge' : ('uDischarge', units.unit1)}
# Instantiate object                  
controls = exodata.ControlFromDF(controls_df, 
                                 vm_controls, 
                                 tz_name = weather.tz_name);
# Collect data
controls.collect_data(start_time, final_time)
# --------------------------------------------------------------------------

# Other Inputs
# --------------------------------------------------------------------------
# Build dataframe
time = pd.to_datetime(start_time)
other_inputs_df = pd.DataFrame(index=[time])
other_inputs_df.index.name = 'Time'
other_inputs_df.loc[time,'uFreDef'] = 0.0
# Define variable map
vm_other_input = {'uFreDef' : ('uFreDef', units.unit1)}
# Instantiate object                  
other_inputs = exodata.OtherInputFromDF(other_inputs_df, 
                                        vm_other_input, 
                                        tz_name = weather.tz_name);
# Collect data
other_inputs.collect_data(start_time, final_time)
# --------------------------------------------------------------------------

# Constraints
# --------------------------------------------------------------------------
# Build dataframe
time = pd.to_datetime(start_time)
constraints_df = pd.DataFrame(index=[time])
constraints_df.index.name = 'Time'
constraints_df.loc[time,'Trtu_max'] = Trtu_max
constraints_df.loc[time,'Trtu_min'] = Trtu_min
constraints_df.loc[time,'Tref_max'] = Tref_max
constraints_df.loc[time,'Tref_min'] = Tref_min
constraints_df.loc[time,'Tfre_max'] = Tfre_max
constraints_df.loc[time,'Tfre_min'] = Tfre_min
constraints_df.loc[time,'SOC_max'] = SOC_max
constraints_df.loc[time,'SOC_min'] = SOC_min
constraints_df.loc[time,'uHeat_max'] = 1.0
constraints_df.loc[time,'uHeat_min'] = 0.0
constraints_df.loc[time,'uCool_max'] = 1.0
constraints_df.loc[time,'uCool_min'] = 0.0
constraints_df.loc[time,'uRef_max'] = 1.0
constraints_df.loc[time,'uRef_min'] = 0.0
constraints_df.loc[time,'uFreCool_max'] = 1.0
constraints_df.loc[time,'uFreCool_min'] = 0.0
constraints_df.loc[time,'uCharge_max'] = 1.0
constraints_df.loc[time,'uCharge_min'] = 0.0
constraints_df.loc[time,'uDischarge_max'] = 1.0
constraints_df.loc[time,'uDischarge_min'] = 0.0
constraints_df.loc[time,'Pnet_max'] = P_demand_limit
# Define variable map
vm_constraints = {'Trtu_max'  : ('Trtu', 'LTE', units.degC),
                  'Trtu_min'  : ('Trtu', 'GTE', units.degC),
                  'Tref_max'  : ('Tref', 'LTE', units.degC),
                  'Tref_min'  : ('Tref', 'GTE', units.degC),
                  'Tfre_max'  : ('Tfre', 'LTE', units.degC),
                  'Tfre_min'  : ('Tfre', 'GTE', units.degC),
                  'SOC_max'   : ('SOC',   'LTE', units.unit1),
                  'SOC_min'   : ('SOC',   'GTE', units.unit1),
                  'uHeat_max' : ('uHeat', 'LTE', units.unit1),
                  'uHeat_min' : ('uHeat', 'GTE', units.unit1),
                  'uCool_max' : ('uCool', 'LTE', units.unit1),
                  'uCool_min' : ('uCool', 'GTE', units.unit1),
                  'uRef_max'  : ('uRef', 'LTE', units.unit1),
                  'uRef_min'  : ('uRef', 'GTE', units.unit1),
                  'uFreCool_max' : ('uFreCool', 'LTE', units.unit1),
                  'uFreCool_min' : ('uFreCool', 'GTE', units.unit1),
                  'uCharge_max' : ('uCharge', 'LTE', units.unit1),
                  'uCharge_min' : ('uCharge', 'GTE', units.unit1),
                  'uDischarge_max' : ('uCharge', 'LTE', units.unit1),
                  'uDischarge_min' : ('uCharge', 'GTE', units.unit1)}
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
if read_pge_tariff:
    solarplus_tariff_obj = SolarPlusCombinedCostCalculator()
    prices_df = solarplus_tariff_obj.get_elec_price((start_time, final_time))  # Get the price of electricity according to the PGE tariffs
    vm_prices = {str(TariffType.ENERGY_CUSTOM_CHARGE.value): ('pi_e', units.dol_kWh),
                 str(TariffType.DEMAND_CUSTOM_CHARGE_SEASON.value): ('pi_d', units.dol_kW),
                 "{0}0".format(str(TariffType.DEMAND_CUSTOM_CHARGE_TOU.value)): ('pi_d', units.dol_kW),  # mid-peak
                 "{0}1".format(str(TariffType.DEMAND_CUSTOM_CHARGE_TOU.value)): ('pi_d', units.dol_kW)  # on-peak
                 }  # Mapping elec price KEYS to a UNIT
else:
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
                        other_inputs = other_inputs.data,
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
                                        'J',
                                        constraint_data = constraints.data,
                                        tz_name = weather.tz_name)
# Set options
opt_options = opt_problem.get_optimization_options()
opt_options['n_e'] = 24*4
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
fig, ax = plt.subplots(5,1,sharex=True)
meas_opt = opt_problem.display_measurements('Simulated')
for meas in ['Trtu', 'Tref', 'Tfre', 'weaTDryBul']:
    ax[0].plot(meas_opt[meas]-273.15, label=meas)
    ax[0].set_title('Temperatures [degC]')
ax[0].legend()
ax[1].plot(meas_opt['SOC'], label='SOC', color='g')
ax[1].set_title('Battery SOC [1]')
ax[1].set_ylim([0,1.25])
for meas in ['Pnet', 'Prtu', 'Pref', 'Pfre', 'Pcharge', 'Pdischarge', 'Ppv']:
    ax[2].plot(meas_opt[meas], label=meas)
ax[2].legend()
ax[2].set_title('Power [W]')
ax[3].plot(prices.display_data(),label='Energy Price')
ax[3].set_title('Electricity Price [$/kWh]')
ax[3].set_ylim([0,15])
for meas in ['uCharge', 'uDischarge', 'uHeat', 'uCool', 'uRef', 'uFreCool']:
    ax[4].plot(meas_opt[meas], label=meas)
ax[4].legend()
ax[4].set_title('Signal [-]')
plt.savefig('process/results/optimal_{0}.png'.format(objective))
plt.show()

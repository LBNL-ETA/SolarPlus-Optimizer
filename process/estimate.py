# -*- coding: utf-8 -*-
"""
This script demonstrates solving the parameter estimation for the store.
"""

from mpcpy import units, variables, exodata, models, systems
import os
from process_data import clean_power_data, clean_temperature_data
from matplotlib import pyplot as plt

# Setup
# --------------------------------------------------------------------------
# Estimation periods
start_time = '4/9/2018 13:00:00' # local time
final_time = '4/9/2018 21:00:00' # local time
local_time = 'America/Los_Angeles'
# Input data
csvpath = '/home/dhb-lx/git/solarplus/SolarPlus-Optimizer/data/Temperature.csv'
# Model definition
mopath = 'models/SolarPlus.mo'
modelpath = 'SolarPlus.Building.Training.Thermal'
# Model measurements
meas_list = ['Trtu', 'Prtu', 'Tref', 'Pref', 'Tfre', 'Pfre']
sample_rate = 300;
# Initial states (must satisfy optimization constraints)
Trtu_0 = 22 # deg C
Tref_0 = 3.5 # deg C
Tfre_0 = -25 # deg C
# --------------------------------------------------------------------------

# Exodata
# --------------------------------------------------------------------------
# Weather
vm_weather = {'Outdoor' : ('weaTDryBul', units.degC)}
geography = (40.88, -124)
csv_weather = '/home/dhb-lx/git/solarplus/SolarPlus-Optimizer/data/Temperature.csv'
weather = exodata.WeatherFromCSV(csv_weather,vm_weather,geography, tz_name=local_time)
weather.collect_data(start_time, final_time);
# Controls
df_power = clean_power_data(start_time, final_time, plot=False)
vm_controls = {'HVAC1_Norm' : ('uCool', units.unit1),
               'RefComp_Norm' : ('uRef', units.unit1),
               'FreComp_Split_Norm' : ('uFreCool', units.unit1),
               'FreHeater_Split_Norm' : ('uFreDef', units.unit1)}
controls = exodata.ControlFromDF(df_power, vm_controls, tz_name = weather.tz_name)
controls.collect_data(start_time, final_time);               
# Parameters
csv_parameters = '/home/dhb-lx/git/solarplus/SolarPlus-Optimizer/models/pars_thermal.csv'
parameters = exodata.ParameterFromCSV(csv_parameters)
parameters.collect_data()
# --------------------------------------------------------------------------

# Measurements
# --------------------------------------------------------------------------
df_temp = clean_temperature_data(start_time, final_time, plot=False)
measurements = dict()
for meas in meas_list:
    measurements[meas] = {'Sample' : variables.Static('{0}_sample'.format(meas), sample_rate, units.s)};
vm_measurements = {'HVAC East_Int' : ('Trtu', units.degC),
                   'Refrigerator West_Int' : ('Tref', units.degC),
                   'Freezer_Int' : ('Tfre', units.degC)}
csv_measurements = '/home/dhb-lx/git/solarplus/SolarPlus-Optimizer/models/temp_clean.csv'
df_temp.to_csv(csv_measurements)
store = systems.RealFromCSV(csv_measurements, measurements, vm_measurements, tz_name = weather.tz_name)
store.collect_measurements(start_time, final_time)
# --------------------------------------------------------------------------

# Model
# --------------------------------------------------------------------------
# Define model information
libraries = os.getenv('MODELICAPATH')
moinfo = (mopath, modelpath, libraries)
# Instantiate object
model = models.Modelica(models.JModelica,
                        models.RMSE,
                        store.measurements,
                        moinfo = moinfo,
                        weather_data = weather.data,
                        control_data = controls.data,
                        parameter_data = parameters.data,
                        tz_name = weather.tz_name)
# --------------------------------------------------------------------------

## Simulate Initial Guess
## --------------------------------------------------------------------------
#model.simulate(start_time, final_time)
#fix,ax = plt.subplots(2,1, sharex=True)
#for key in model.measurements.keys():
#    if model.measurements[key]['Simulated'].get_base_unit_name() is 'K':
#        x = 0
#        y = -273.15
#    else:
#        x = 1    
#        y = 0
#    ax[x].plot(model.display_measurements('Simulated')[key]+y, label=key)
#    ax[x].legend()
#plt.show()
## --------------------------------------------------------------------------

# Solve
# --------------------------------------------------------------------------
# Solve estimation problem
model.estimate(start_time, final_time, ['Trtu','Tref','Tfre'])
model.validate(start_time, final_time, 'validate', plot=1)
plt.close('all')
for key in ['Trtu','Tref','Tfre']:
    plt.plot(model.measurements[key]['Simulated'].get_base_data()-273.15, label=key+'_Simulated')
    plt.plot(model.measurements[key]['Measured'].get_base_data()-273.15, label=key+'_Measured')
    plt.legend()
plt.show()
# --------------------------------------------------------------------------
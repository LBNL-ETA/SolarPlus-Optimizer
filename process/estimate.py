# -*- coding: utf-8 -*-
"""
This script demonstrates solving the parameter estimation for the store.
"""

from mpcpy import units, variables, exodata, models, systems
import os
#from process_data import clean_power_data, clean_temperature_data
from matplotlib import pyplot as plt

# Setup
# --------------------------------------------------------------------------
# Estimation periods
start_time = '2019-11-06 08:00:00+00:00' # UTC time
final_time = '2019-11-06 10:00:00+00:00' # UTC time
# local_time = 'America/Los_Angeles'
# Model definition
mopath = 'models/SolarPlus.mo'
modelpath = 'SolarPlus.Building.Training.Thermal'
# Model measurements
meas_list = ['Trtu', 'Tref', 'Tfre']
sample_rate = 300;
# Initial states (must satisfy optimization constraints)
Trtu_0 = 295.59 # deg C
Tref_0 = 274.48 # deg C
Tfre_0 = 252.82 # deg C
# Simulate Initial Option
simulate_initial = False
# --------------------------------------------------------------------------

# Exodata
# --------------------------------------------------------------------------
# Weather
vm_weather = {'temperature_k' : ('weaTDryBul', units.K),
              'poa_win': ('weaPoaWin', units.W_m2),
              'poa_pv': ('weaPoaPv', units.W_m2)}
geography = (37.8771, -122.2485)
csv_weather = 'controller/validation/weather_input_201911.csv'
weather = exodata.WeatherFromCSV(csv_weather,vm_weather,geography, tz_name='UTC')
weather.collect_data(start_time, final_time);
# Controls
vm_controls = {'HVAC1_Norm' : ('uCool', units.unit1),
               'RefComp_Norm' : ('uRef', units.unit1),
               'FreComp_Split_Norm' : ('uFreCool', units.unit1),
               'uFreDef' : ('uFreDef', units.unit1)}
csv_power = 'controller/validation/normalized_power_201911.csv'
controls = exodata.ControlFromCSV(csv_power, vm_controls, tz_name=weather.tz_name)
controls.collect_data(start_time, final_time);
# Parameters
csv_parameters = 'models/pars_thermal.csv'
parameters = exodata.ParameterFromCSV(csv_parameters)
parameters.collect_data()
# --------------------------------------------------------------------------

# Measurements
# --------------------------------------------------------------------------
measurements = dict()
for meas in meas_list:
    measurements[meas] = {'Sample' : variables.Static('{0}_sample'.format(meas), sample_rate, units.s)};
vm_measurements = {'temp_rtu_west_k' : ('Trtu', units.K),
                   'ref_k' : ('Tref', units.K),
                   'fre_k' : ('Tfre', units.K)}
csv_measurements = 'controller/validation/temperature_201911.csv'
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

# Simulate Initial Guess
# --------------------------------------------------------------------------
if simulate_initial:
    model.simulate(start_time, final_time)
    fix,ax = plt.subplots(2,1, sharex=True)
    for key in model.measurements.keys():
        if model.measurements[key]['Simulated'].get_base_unit_name() is 'K':
            x = 0
            y = -273.15
        else:
            x = 1
            y = 0
        ax[x].plot(model.display_measurements('Simulated')[key]+y, label=key)
        ax[x].legend()
    plt.show()
# --------------------------------------------------------------------------

# Solve
# --------------------------------------------------------------------------
# Solve estimation problem
model.estimate(start_time, final_time, ['Trtu','Tref','Tfre'])
print(model.display_measurements('Measured'))
for key in model.parameter_data.keys():
    print(key, model.parameter_data[key]['Value'].display_data())
model.validate(start_time, final_time, 'validate', plot=0)
for key in ['Trtu','Tref','Tfre']:
    plt.plot(model.measurements[key]['Simulated'].get_base_data()-273.15, label=key+'_Simulated')
    plt.plot(model.measurements[key]['Measured'].get_base_data()-273.15, label=key+'_Measured')
    plt.legend()
plt.show()
# --------------------------------------------------------------------------

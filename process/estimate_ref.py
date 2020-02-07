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
start_time = '2019-11-12 00:00:00+00:00' # UTC time
final_time = '2019-11-12 18:00:00+00:00' # UTC time
start_time_validate = '2019-11-07 15:00:00+00:00'
final_time_validate = '2019-11-07 17:00:00+00:00'
# local_time = 'America/Los_Angeles'
# Model definition
mopath = 'models/SolarPlus.mo'
modelpath = 'SolarPlus.Building.Training.Refrigeration'
# Model measurements
meas_list = ['Tfre', 'Tref']
sample_rate = 300;
# Initial states (must satisfy optimization constraints)
Tfre_0 = 252.48 # K
Tref_0 = 274.48 # K
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
vm_controls = {'temp_rtu_west_k': ('Trtu_west', units.K),
               'temp_rtu_east_k' : ('Trtu_east', units.K),
               'freezer_CompressorStatus' : ('uFreCool', units.unit1),
               # 'FreComp_Split_Norm' : ('uFreCool', units.unit1),
               'uFreDef' : ('uFreDef', units.unit1),
               'refrigerator_CompressorStatus' : ('uRef', units.unit1)}
csv_power = 'controller/validation/normalized_power_201911.csv'
controls = exodata.ControlFromCSV(csv_power, vm_controls, tz_name='UTC')
controls.collect_data(start_time, final_time);
plt.figure(1)
plt.subplot(2,1,1)
plt.plot(controls.get_base_data()['uFreCool'])
plt.plot(controls.get_base_data()['uFreDef'])
plt.plot(controls.get_base_data()['uRef'])
plt.legend(['Freezer','Freezer defrost'],loc='best')
plt.subplot(2,1,2)
plt.plot(controls.get_base_data()['Trtu_east']-273.15)
plt.plot(controls.get_base_data()['Trtu_west']-273.15)
plt.legend()

# Parameters
csv_parameters = 'models/pars_ref.csv'
parameters = exodata.ParameterFromCSV(csv_parameters)
parameters.collect_data()

# --------------------------------------------------------------------------

# Measurements
# --------------------------------------------------------------------------
measurements = dict()
for meas in meas_list:
    measurements[meas] = {'Sample' : variables.Static('{0}_sample'.format(meas), sample_rate, units.s)};
vm_measurements = {'fre_k' : ('Tfre', units.K),
                   'ref_k': ('Tref', units.K)}
csv_measurements = 'controller/validation/temperature_201911.csv'
store = systems.RealFromCSV(csv_measurements, measurements, vm_measurements, tz_name = weather.tz_name)
store.collect_measurements(start_time, final_time)
# plt.figure(4)
# plt.plot(store.get_base_measurements(vm_measurements))
# plt.legend()
# plt.show()
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

emulation = systems.EmulationFromFMU(measurements,
                                     moinfo=moinfo,
                                     weather_data = weather.data,
                                     control_data = controls.data,
                                     tz_name = weather.tz_name)

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
model.estimate(start_time, final_time, ['Tfre','Tref'])
# print(model.display_measurements('Measured'))

# emulation.collect_measurements(start_time_validate, final_time_validate)
# model.measurements = emulation.measurements
model.validate(start_time, final_time, 'validate', plot=0)
plt.figure(2)
plt.subplot(2,1,1)
plt.plot(model.measurements['Tfre']['Simulated'].get_base_data()-273.15, label='Tfre_Simulated')
plt.plot(model.measurements['Tfre']['Measured'].get_base_data()-273.15, label='Tfre_Measured')
plt.legend()
plt.subplot(2,1,2)
plt.plot(model.measurements['Tref']['Simulated'].get_base_data()-273.15, label='Tref_Simulated')
plt.plot(model.measurements['Tref']['Measured'].get_base_data()-273.15, label='Tref_Measured')
plt.legend()
plt.show()

print('\n')
print("-------------------------------------")
print("The RMSE value of the estimation are:")
for key in ['Tfre','Tref']:
    print(model.RMSE[key].display_data())

print('\n')
print("--------------------------------------")
print("The estimated parameters for the model are:")
for key in model.parameter_data.keys():
    print(key, model.parameter_data[key]['Value'].display_data())
print("--------------------------------------")
# --------------------------------------------------------------------------

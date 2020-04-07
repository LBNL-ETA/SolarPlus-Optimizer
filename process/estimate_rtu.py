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
final_time = '2019-11-12 09:00:00+00:00' # UTC time
start_time_validate = '2019-11-14 00:00:00+00:00'
final_time_validate = '2019-11-15 00:00:00+00:00'
# local_time = 'America/Los_Angeles'
# Model definition
mopath = 'models/SolarPlus.mo'
modelpath = 'SolarPlus.Building.Training.RTU'
# Model measurements
# meas_list = ['Trtu_west', 'Trtu_east', 'Tref', 'Tfre']
meas_list = ['Trtu_west', 'Trtu_east']
sample_rate = 300;
# Initial states (must satisfy optimization constraints)
Trtu_west_0 = 295.14 # 2019-11-12 00:00
Trtu_east_0 = 296.68 # 2019-11-12 00:00
# Trtu_west_0 = 294.39 # 2019-11-12 04:00
# Trtu_east_0 = 295.26 # 2019-11-12 04:00

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
fig1 = plt.figure(1)
plt.plot(weather.get_base_data()['weaTDryBul']-273.15,label='TOut')
plt.legend()
fig1.savefig('pe_Outdoor temperature')
fig2 = plt.figure(2)
plt.plot(weather.get_base_data()['weaPoaWin'],label='Window solar radiation')
# plt.plot(weather.get_base_data()['weaPoaPv'],label='PV solar radiation')
plt.legend()
fig2.savefig("pe_Solar radiation on windows")

# Controls
vm_controls = {'HVAC_West_Norm' : ('uCoolWest', units.unit1),
               'HVAC_East_Norm' : ('uCoolEast', units.unit1),
               'ref_k' : ('Tref', units.K),
               'fre_k': ('Tfre', units.K),
               'internal_gains_con': ('intGai', units.W)}
               # 'freezer_CompressorStatus' : ('uFreCool', units.unit1),
               # 'FreComp_Split_Norm' : ('uFreCool', units.unit1),
               # 'uFreDef' : ('uFreDef', units.unit1),
               # 'RefComp_Norm' : ('uRef', units.unit1)}
               # 'refrigerator_CompressorStatus' : ('uRef', units.unit1)}
csv_power = 'controller/validation/normalized_power_201911.csv'
controls = exodata.ControlFromCSV(csv_power, vm_controls, tz_name=weather.tz_name)
controls.collect_data(start_time, final_time);
fig3 = plt.figure(3)
plt.plot(controls.get_base_data()['uCoolWest'])
plt.plot(controls.get_base_data()['uCoolEast'])
plt.legend(['RTU_west','RTU_east'],loc='best')
fig3.savefig("pe_Cooling control signal")
fig4 = plt.figure(4)
plt.plot(controls.get_base_data()['intGai'])
fig4.savefig("pe_Internal Gains")
# Parameters
csv_parameters = 'models/pars_rtu.csv'
parameters = exodata.ParameterFromCSV(csv_parameters)
parameters.collect_data()

# --------------------------------------------------------------------------

# Measurements
# --------------------------------------------------------------------------
measurements = dict()
for meas in meas_list:
    measurements[meas] = {'Sample' : variables.Static('{0}_sample'.format(meas), sample_rate, units.s)};
vm_measurements = {'temp_rtu_west_k' : ('Trtu_west', units.K),
                   'temp_rtu_east_k' : ('Trtu_east', units.K)}
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
# opt_options = model._estimate_method.opt_problem.get_optimization_options()
opt_options = model._parameter_estimate_method.opt_problem.get_optimization_options()
opt_options['IPOPT_options']['ma27_liw_init_factor'] = 5*16
opt_options['IPOPT_options']['ma27_la_init_factor'] = 5*16
opt_options['IPOPT_options']['max_iter'] = 3000
#opt_options['IPOPT_options']['tol'] = 0.00001
# model._estimate_method.opt_problem.set_optimization_options(opt_options)
model._parameter_estimate_method.opt_problem.set_optimization_options(opt_options)
model.parameter_estimate(start_time, final_time, ['Trtu_west','Trtu_east'], global_start=0, seed=None)
model.validate(start_time, final_time, 'validate', plot=1)
fig = plt.figure(5)
plt.subplot(2,1,1)
plt.plot(model.measurements['Trtu_west']['Simulated'].get_base_data()-273.15, label='Trtu_west_Simulated')
plt.plot(model.measurements['Trtu_west']['Measured'].get_base_data()-273.15, label='Trtu_west_Measured')
plt.legend()
plt.subplot(2,1,2)
plt.plot(model.measurements['Trtu_east']['Simulated'].get_base_data()-273.15, label='Trtu_east_Simulated')
plt.plot(model.measurements['Trtu_east']['Measured'].get_base_data()-273.15, label='Trtu_east_Measured')
plt.legend()
# plt.show()
fig.savefig("pe_Temperature validation")

print('\n')
print("-------------------------------------")
print("The RMSE value of the estimation is:")
for key in ['Trtu_west','Trtu_east']:
    print(model.RMSE[key].display_data())
print('\n')
print("--------------------------------------")
print("The estimated parameters for the model are:")
for key in model.parameter_data.keys():
    print(key, model.parameter_data[key]['Value'].display_data())

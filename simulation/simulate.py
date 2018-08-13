# -*- coding: utf-8 -*-
"""
This script runs a simulation of the MPC controller for the convenience
store.  A version of the MPC model with feedback control is used to 
represent the real building.

"""

from mpcpy import exodata, units
import os
from datetime import timedelta
import pandas as pd
import numpy as np
from controller import mpc

# Setup
# ==========================================================================
sim_start_time = '6/1/2018 00:00:00'
sim_final_time = '6/2/2018 00:00:00'
tz_name = 'America/Los_Angeles'
sim_control_step = 1*3600
controller = 'mpc'
mpc_horizon = 24*3600

# Initialize
# ==========================================================================
# Create output directory
cwd = os.getcwd()
outdir = os.path.join('simulation', 'output')
# Exodata times
start_time_exo = pd.to_datetime(sim_start_time).tz_localize(tz_name)
final_time_exo = pd.to_datetime(sim_final_time).tz_localize(tz_name) + timedelta(seconds=mpc_horizon)
# Weather
csvpath = os.path.join('data','Temperature.csv')
weather_vm = {'Outdoor':('weaTDryBul', units.degC)}
geography = (40.88,-124.0)
weather = exodata.WeatherFromCSV(csvpath, weather_vm, geography, tz_name = tz_name)
weather.collect_data(start_time_exo, final_time_exo);
# Setpoints
time_format = '%m/%d/%Y %H:%M:%S'
index = pd.date_range(start_time_exo.strftime(time_format), 
                      final_time_exo.strftime(time_format), 
                      freq ='H');
data = index.hour;
setpoints_df = pd.DataFrame(data = data, index = index, columns=['Hour']);
setpoints_df['coolSet'] = np.where((setpoints_df['Hour'] >= 0) & (setpoints_df['Hour'] <= 25), 24, 28);
setpoints_df['heatSet'] = np.where((setpoints_df['Hour'] >= 0) & (setpoints_df['Hour'] <= 25), 21, 15);
setpoints_vm = {'coolSet': ('coolSet', units.degC), \
                'heatSet': ('heatSet', units.degC)};
setpoints = exodata.OtherInputFromDF(setpoints_df, setpoints_vm, tz_name = weather.tz_name);
setpoints.collect_data(start_time_exo, final_time_exo);
# Define simulation steps
sim_steps = pd.date_range(sim_start_time,
                          sim_final_time,
                          freq = '{0}s'.format(sim_control_step)).tz_localize(weather.tz_name)                        
iterations = range(len(sim_steps))
# Save setup
with open(outdir+'/mpc_setup.txt', 'w') as f:
    f.write(str(sim_start_time) +'\n')
    f.write(str(sim_final_time) +'\n')
    f.write(str(sim_control_step) +'\n')
    f.write(str(mpc_horizon) +'\n')
    f.write(weather.tz_name +'\n')
weather.display_data().to_csv(os.path.join(outdir,'weather.csv'), index_label = 'Time')
setpoints.display_data().to_csv(os.path.join(outdir,'setpoints.csv'), index_label = 'Time')
# Instantiate controller
if controller is 'mpc':
    controller = mpc()
## Start loop
## ----------
#for i in iterations[:-1]:
#    # Set optimization horizon time
#    opt_start_time = sim_steps[i]
#    opt_final_time = sim_steps[i]+timedelta(seconds=mpc_horizon)
#    print('\n%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%')
#    print('Running simulation step {0} to {1}...'.format(sim_steps[i], sim_steps[i+1]))
#    print('Optimization horizon is {0} to {1}...'.format(opt_start_time, opt_final_time))
#    # Set states and warm start if not initial simulation
#    # ---------------------------------------------------
#    # State estimate
#    # ----------------------------------
#    # Define initial parameters and states
#    if 'R1C1' in t_mod:
#        par_init = {'zone.T0_C' : 'zone.air.T'}
#    elif 'R2C2' in t_mod:
#        par_init = {'zone.T0_C' : 'zone.air.T',
#                    'zone.T0_Ci' : 'zone.intMass.T'}
#    elif ('R3C3' in t_mod) or ('R4C3' in t_mod):
#        par_init = {'zone.T0_C' : 'zone.air.T',
#                    'zone.T0_Ci' : 'zone.intMass.T',
#                    'zone.T0_Ce' : 'zone.extMass.T'}
#    elif ('R4C4' in t_mod) or ('R5C4' in t_mod):
#        par_init = {'zone.T0_C' : 'zone.air.T',
#                    'zone.T0_Ci' : 'zone.intMass.T',
#                    'zone.T0_Ce' : 'zone.extMass.T',
#                    'zone.T0_Cem' : 'zone.extMass1.T'}
#    else:
#        raise ValueError('Model {0} unknown.'.format(t_mod[0:4]))
#    # Set initial parameters with states
#    ini_time_utc = pd.to_datetime(sim_steps[i]).tz_convert('utc')
#    for par in par_init.keys():
#        if par == 'zone.T0_C':
#            # Set as measured air temperature
#            value = emulation_mpc.get_base_measurements('Measured')['Tzone'].get_values()[-1]
#            # Adjust LTE constraints of initial time if neccessary
#            ts = opt_problem.constraint_data['Tzone']['LTE'].get_base_data()
#            if value >= ts.loc[sim_steps[i]]:
#                with open(case_dir + '/constraint_violation.txt', 'a') as f:
#                    f.write(str(sim_steps[i]) + ': ' + str(value) + ',' + str(ts.loc[sim_steps[i]]) + '\n')
#                ts.loc[sim_steps[i]] = value+0.001
#                opt_problem.constraint_data['Tzone']['LTE'].set_data(ts)
#            # Adjust LTE constraints of initial time if neccessary
#            ts = opt_problem.constraint_data['Tzone']['GTE'].get_base_data()
#            if value <= ts.loc[sim_steps[i]]:
#                with open(case_dir + '/constraint_violation.txt', 'a') as f:
#                    f.write(str(sim_steps[i]) + ': ' + str(value) + ',' + str(ts.loc[sim_steps[i]]) + '\n')
#                ts.loc[sim_steps[i]] = value-0.001
#                opt_problem.constraint_data['Tzone']['GTE'].set_data(ts)
#            
#        else:
#            # Set as estimated state
#            def estimate(method):
#                if (method is 'simple') or (i==0):
#                    value = emulation_mpc.get_base_measurements('Measured')['Tzone'].get_values()[-1]                              
#                elif method is 'model':
#                    data = model._res[par_init[par]];
#                    time = model._res['time'];
#                    timedelta = pd.to_timedelta(time-time[0], 's');
#                    timeindex = model.start_time_utc + timedelta;
#                    ts = pd.Series(data = data, index = timeindex);
#                    value = ts.loc[ini_time_utc]
#
#                return value
#                
#            value = estimate('model')
#            
#        print('Setting {0} as {1}.'.format(par, value))
#        model.parameter_data[par] = dict()
#        model.parameter_data[par]['Value'] = variables.Static(par+'_value', value, units.K)
#        model.parameter_data[par]['Free'] = variables.Static(par+'_free', False, units.boolean)
#        # Set controls to previous optimization result shifted to new time
#        # ----------------------------------------------------------------
#        for key in model.control_data.keys():
#            # Get previous timestep optimal controls
#            opt_con = model.control_data[key].get_base_data().loc[opt_start_time:]
#            # Create new index reference to current step
#            delta = pd.to_timedelta(opt_con.index.values-opt_con.index.values[0])
#            index = sim_steps[i]+delta
#            # Get data
#            data = opt_con.get_values()
#            # Get unit
#            unit = model.control_data[key].get_base_unit()
#            # Create ts variable
#            ts = pd.Series(data=data, index=index)
#            # Set new control
#            model.control_data[key] = variables.Timeseries(key, ts, unit)
#    # Solve optimal control problem
#    # -----------------------------
#    # Solve
#    opt_problem.optimize(opt_start_time, opt_final_time, price_data = prices.data)
#    opt_statistics = opt_problem.get_optimization_statistics()
#    # Save data
#    df_opt_res = opt_problem.display_measurements('Simulated')
#    df_opt_res.to_csv(case_dir+'/optimal_result_{0}.csv'.format(i))
#    if i == 0:
#        open_as = 'w'
#    else:
#        open_as = 'a'
#    with open(case_dir+'/optimal_statistics.txt', open_as) as f:
#        f.write(str(sim_steps[i]) + ': ' +  str(opt_statistics) + '\n')
#    # Simulate model with optimal control
#    if opt_problem._problem_type.__class__.__name__ is 'EnergyCostMin':
#        model.other_inputs = dict()
#    model.simulate(opt_start_time, opt_final_time)
#    # Save data
#    df_opt = model.display_measurements('Simulated')
#    df_opt['uHeat_con'] = model.control_data['uHeat'].get_base_data()
#    df_opt['uCool_con'] = model.control_data['uCool'].get_base_data()
#    df_opt.to_csv(case_dir+'/optimal_model_control_{0}.csv'.format(i))
#    # Simulate mpc emulation for control step
#    # ---------------------------------------
#    # Set controls in emulation
#    if mpc_emu == 'open':
#        emulation_mpc.control_data = model.control_data
#    elif mpc_emu == 'closed':
#        # Make setpoints
#        # Get temperature trajectory from mpc
#        sp_mpc_df = pd.DataFrame()
#        sp_mpc_df['coolSet_mpc'] = df_opt_res['Tzone']+dsp
#        sp_mpc_df['heatSet_mpc'] = df_opt_res['Tzone']-dsp
#        sp_mpc_df = sp_mpc_df.tz_convert(weather.tz_name).tz_localize(None)
#        # Make sure setpoints within constraints and keep heating to only if necessary
#        setpoints_mpc_df = pd.DataFrame(columns=['coolSet_mpc', 'heatSet_mpc'])
#        for j in setpoints_df.loc[opt_start_time.tz_localize(None):opt_final_time.tz_localize(None)].index:
#            coolSet = min([sp_mpc_df.loc[j,'coolSet_mpc'],setpoints_df.loc[j,'coolSet']])
#            heatSet = setpoints_df.loc[j,'heatSet']
#            setpoints_mpc_df.loc[j,'coolSet_mpc'] = coolSet
#            setpoints_mpc_df.loc[j,'heatSet_mpc'] = heatSet
#        variable_map_setpoints_mpc = {'coolSet_mpc': ('coolSet', units.K), \
#                                      'heatSet_mpc': ('heatSet', units.K)}
#        setpoints_mpc = exodata.OtherInputFromDF(setpoints_mpc_df, variable_map_setpoints_mpc, tz_name = weather.tz_name);
#        setpoints_mpc.collect_data(opt_start_time, opt_final_time);
#        # Save data
#        setpoints_mpc_df.to_csv(case_dir+'/optimal_setpoints_{0}.csv'.format(i))
#        # Set setpoints
#        emulation_mpc.other_inputs = setpoints_mpc.data
#    else:
#        raise ValueError('MPC emulation model identifier {0} not recognized.'.format(mpc_emu))
#    # Set time
#    emu_final_time = sim_steps[i+1]
#    # Simulate
#    emulation_mpc.collect_measurements('continue', emu_final_time)
#    # Save results
#    if mpc_emu == 'open':
#        df_mpc = emulation_mpc.display_measurements('Measured')
#    elif mpc_emu == 'closed':
#        df_mpc = emulation_mpc.display_measurements('Measured')
#    df_mpc.to_csv(case_dir+'/mpc_control_{0}.csv'.format(i))

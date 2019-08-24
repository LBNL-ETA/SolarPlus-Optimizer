# -*- coding: utf-8 -*-
"""
This script runs the MPC controller in real time.

"""

import os
import datetime
import pandas as pd
import numpy as np
import mpc_config_control as mpc_config
from mpc import mpc
from database_client.data_client import Data_Client

control_start = True
init = True
while control_start:
    # Setup
    # ==============================================================================
    controller = 'mpc'
    start_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:00")
    start_time = pd.to_datetime(start_time)
    mpc_horizon = 24*3600
    mpc_step = 3600
    print('\n%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%')
    print("The Solar+ Optimizer has begun its operation...")
    print("The prediction horizon is {} hours.".format(mpc_horizon/3600))
    print('\n')

    # Initialize
    # ==============================================================================
    # Create output folder under the current directory
    outdir = os.path.abspath(os.path.join(__file__,'..','output'))
    if not os.path.exists(outdir):
        os.mkdir(outdir)
    # Save setup: UTC time
    with open(outdir+'/mpc_setup.txt', 'w') as f:
        f.write(str(start_time) +'\n')
        f.write(str(mpc_step) +'\n')
        f.write(str(mpc_horizon) +'\n')

    # Instantiate controller
    if controller is 'mpc':
        config = mpc_config.get_config()
        controller = mpc(config['model_config'],
                         config['opt_config'],
                         config['system_config'],
                         weather_config = config['weather_config'],
                         control_config = config['control_config'],
                         setpoints_config = config['setpoints_config'],
                         constraint_config = config['constraint_config'],
                         data_manager_config = config['data_manager_config'],
                         price_config = config['price_config'])
        print('The controller is instantiating...')

    # Get system states from measurements of last time step
    # sampling rate is 5 minutes
    # get states from thermostats, refrigerator and freezer controllers
    client = Data_Client()
    parker_controller_variables = ['CabinetTemperature']
    thermostat_variables = ['space_temp']
    previous_time = start_time - datetime.timedelta(minutes=30)
    end_time = start_time - datetime.timedelta(minutes=start_time.minute % 5)
    parker_df = client.get_device_data(device_type='parker_controllers', start_time=previous_time, end_time=end_time, variables=parker_controller_variables, resample_window='5T')
    thermostat_df = client.get_device_data(device_type='thermostats', start_time=previous_time, end_time=end_time, variables=thermostat_variables, resample_window='5T')
    # Save per configuration
    states_time = end_time
    df_last_states = pd.DataFrame({'Time':[states_time]})
    df_last_states.set_index('Time', inplace=True)
    df_last_states.to_csv(outdir+'/initial_states.csv')
    for state in config['model_config']['init_vm']:
        value = controller.parameter.display_data().loc[state,'Value']
        df_last_states[config['model_config']['init_vm'][state]] = value
    df_last_states[config['model_config']['init_vm']['Tref_0']] = parker_df['refrigerator_CabinetTemperature'][-1]
    df_last_states[config['model_config']['init_vm']['Tfre_0']] = parker_df['freezer_CabinetTemperature'][-1]
    df_last_states[config['model_config']['init_vm']['Trtu_0']] = thermostat_df['thermostat_west_space_temp'][-1]

    # df_last_states.to_csv(os.path.abspath(os.path.join(__file__,'..','..','data','emulation_states.csv')))
    print("The last system states measurements sent to the controller are:")
    print(df_last_states)
    print('\n')

    # Control Loop
    # ==============================================================================
    # Solve optimal control problem
    final_time = start_time + datetime.timedelta(seconds=mpc_step)
    control, measurements, other_outputs, statistics = controller.optimize(start_time, final_time, init=init)
    # Save optimization result data
    control.to_csv(outdir+'/control_{0}.csv'.format(i))
    measurements.to_csv(outdir+'/measurements_{0}.csv'.format(i))
    other_outputs.to_csv(outdir+'/other_outputs_{0}.csv'.format(i))
    if init == True:
        open_as = 'w'
    else:
        open_as = 'a'
    with open(outdir+'/optimal_statistics_{0}.txt'.format(i), open_as) as f:
        f.write(str(sim_steps[i]) + ': ' +  str(statistics) + '\n')
    # Push setpoints
    setpoints = controller.set_setpoints(control, measurements)
    setpoints.to_csv(outdir+'/setpoints_{0}.txt'.format(i))
    # check if setpoints have been pushed successefully; then wait for the next control loop
    end_time = datetime.datetime.now()
    control_loop_time = (end_time - start_time).total_seconds()
    print('This control loop has taken {} min'.format(control_loop_time/60))
    # if the optimization takes reasonable time; continue the process
    init = False
    if control_loop_time > mpc_step:
        break

# -*- coding: utf-8 -*-
"""
This script runs the MPC controller in real time.

"""

import os
import time
import pandas as pd
import numpy as np
import mpc_config_control as mpc_config
from mpc import mpc

# Setup
# ==============================================================================
mpc_start = True
controller = 'mpc'
start_time = time.time()
mpc_horizon = 24*3600
mpc_step = 3600
if mpc_start:
    print('\n%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%')
    print("The Solar+ Optimizer has begun its optimization...")
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
    f.write(str(pd.to_datetime(start_time,unit='s')) +'\n')
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

# Get states and names from configuration
start_time_dt = pd.to_datetime(start_time, unit='s', utc=True).replace(microsecond=0)
df_init_states = pd.DataFrame({'Time':[start_time_dt]})
df_init_states.set_index('Time', inplace=True)
for state in config['model_config']['init_vm']:
    value = controller.parameter.display_data().loc[state,'Value']
    df_init_states[config['model_config']['init_vm'][state]] = value
# Save per configuration
df_init_states.to_csv(outdir+'/initial_states.csv')
# df_init_states.to_csv(os.path.abspath(os.path.join(__file__,'..','..','data','emulation_states.csv')))
print("The initial system states are:")
print(df_init_states)
print('\n')

# Control Loop
# ==============================================================================
while mpc_start:
    init = True
    i = 0
    # Solve optimal control problem
    final_time = start_time + mpc_step
    final_time_dt = pd.to_datetime(final_time, unit='s', utc=True).replace(microsecond=0)
    control, measurements, other_outputs, statistics = controller.optimize(start_time_dt, final_time_dt, init=init)
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
    break
    end_time = time.time()
    control_loop_time = (end_time - start_time)/60
    print('This control loop has taken {} min'.format(control_loop_time))
    # if the optimization takes reasonable time; continue the process
    if end_time < final_time:
        continue
        start_time = final_time + mpc_step
        init = False
        i = i+1

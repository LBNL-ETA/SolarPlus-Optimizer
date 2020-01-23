# -*- coding: utf-8 -*-
"""
This script runs a simulation of the MPC controller for the convenience
store.  A version of the MPC model with feedback control is used to
represent the real building.

"""

from mpcpy import exodata, units, systems, variables
import os
from datetime import timedelta
import pandas as pd
import numpy as np
from controller.mpc import mpc
import mpc_simulation_config as mpc_config
from emulator import emulator
import pytz

# Setup
# ==========================================================================
sim_start_time = '6/1/2018 00:00:00'
sim_final_time = '6/2/2018 00:00:00'
tz_name = 'America/Los_Angeles'
sim_control_step = 1*3600
controller = 'mpc'
mpc_horizon = 24*3600
emulation_states_csv = "data/emulation_states.csv"

# Initialize
# ==========================================================================
# Create output directory
cwd = os.getcwd()
outdir = os.path.join('simulation', 'output')
# Define simulation steps
sim_steps = pd.date_range(sim_start_time,
                          sim_final_time,
                          freq = '{0}s'.format(sim_control_step))
tz_local = pytz.timezone("America/Los_Angeles")
tz_utc = pytz.timezone("UTC")

sim_steps = sim_steps.tz_localize(tz_local).tz_convert(tz_utc)

iterations = range(len(sim_steps))
# Save setup
with open(outdir+'/mpc_setup.txt', 'w') as f:
    f.write(str(sim_start_time) +'\n')
    f.write(str(sim_final_time) +'\n')
    f.write(str(sim_control_step) +'\n')
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

# Instantiate emulator to None
emu = None
#use_data_manager_in_emulator = config.get("use_data_manager_in_emulator", False)
use_data_manager_in_emulator = config.get("use_data_manager_in_emulator", False)

# Initialize emulator states for controller
# Remove previous simulation if exists
if os.path.exists(emulation_states_csv):
    os.remove(emulation_states_csv)
# Get states and names from configuration
initial_states = []
initial_names = []
df_initial_states = pd.DataFrame(index=[sim_steps[0]])
df_initial_states.index.name = 'Time'
for state in config['model_config']['init_vm']:
    value = controller.parameter.display_data().loc[state,'Value']
    df_initial_states[config['model_config']['init_vm'][state]] = value
# Save per configuration
df_initial_states.to_csv(emulation_states_csv)


# Simulation Loop
# ==========================================================================
for i in iterations[:-1]:
    # Set optimization horizon time
    opt_start_time = sim_steps[i]
    opt_final_time = sim_steps[i]+timedelta(seconds=mpc_horizon)
    print('\n%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%')
    print('Running simulation step {0} to {1}...'.format(sim_steps[i], sim_steps[i+1]))
    print('Optimization horizon is {0} to {1}...'.format(opt_start_time, opt_final_time))
    # Solve optimal control problem
    if i is 0:
        init = True
    else:
        init = False
    control, measurements, other_outputs, statistics = controller.optimize(opt_start_time, opt_final_time, init=init)
    # Save optimization result data
    control.to_csv(outdir+'/control_{0}.csv'.format(i))
    measurements.to_csv(outdir+'/measurements_{0}.csv'.format(i))
    other_outputs.to_csv(outdir+'/other_outputs_{0}.csv'.format(i))
    if i == 0:
        open_as = 'w'
    else:
        open_as = 'a'
    with open(outdir+'/optimal_statistics_{0}.txt'.format(i), open_as) as f:
        f.write(str(sim_steps[i]) + ': ' +  str(statistics) + '\n')
    # Push setpoints
    setpoints = controller.set_setpoints(control, measurements)
#    # Simulate optimal control to check
#    sim_measurements, sim_other_outputs = controller.simulate(opt_start_time, opt_final_time, optimal=True)
#    # Save optimization simulation data
#    sim_measurements.to_csv(outdir+'/sim_measurements_{0}.csv'.format(i))
#    sim_other_outputs.to_csv(outdir+'/sim_other_outputs_{0}.csv'.format(i))
    # Simulate emulator
    emu_final_time = sim_steps[i+1]
    if i is 0:
        emu_start_time = sim_steps[i]
    else:
        emu_start_time = 'continue'

    if emu == None:
        # Instantiate emulator
        emu = emulator(use_data_manager_in_emulator=use_data_manager_in_emulator, data_manager=controller.data_manager, outdir=outdir)

    emu_measurements = emu.simulate(emu_start_time, emu_final_time)
    # Save emulator data
    emu_measurements.to_csv(outdir+'/emu_measurements_{0}.csv'.format(i))
    # Output emulation states
    emu_measurements.to_csv('data/emulation_states.csv')

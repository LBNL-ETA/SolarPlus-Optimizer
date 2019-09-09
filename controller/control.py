# -*- coding: utf-8 -*-
"""
This script runs the MPC controller in real time.

"""

import os
import datetime
import time
import pandas as pd
import numpy as np
import mpc_config_control as mpc_config
from mpc import mpc

tz_computer = 'America/New_York'
control_start = True
init = True
i = 1
while control_start:
    # Setup
    # ==============================================================================
    controller = 'mpc'
    start = datetime.datetime.now()
    start_time = start.strftime("%Y-%m-%d %H:00:00")
    start_time_utc = pd.to_datetime(start_time).tz_localize(tz_computer).tz_convert('UTC')
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
        f.write(str(start_time_utc) +'\n')
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

    # Control Loop
    # ==============================================================================
    # Solve optimal control problem
    final_time_utc = start_time_utc + datetime.timedelta(seconds=mpc_horizon)
    control, measurements, other_outputs, statistics = controller.optimize(start_time_utc, final_time_utc, init=init)
    # Save optimization result data
    control.to_csv(outdir+'/control_{0}.csv'.format(i))
    measurements.to_csv(outdir+'/measurements_{0}.csv'.format(i))
    other_outputs.to_csv(outdir+'/other_outputs_{0}.csv'.format(i))
    if init == True:
        open_as = 'w'
    else:
        open_as = 'a'
    with open(outdir+'/optimal_statistics_{0}.txt'.format(i), open_as) as f:
        f.write(str(statistics) + '\n')
    # Push setpoints
    setpoints = controller.set_setpoints(control, measurements)
    setpoints.to_csv(outdir+'/setpoints_{0}.txt'.format(i))
    # check if setpoints have been pushed successefully; then wait for the next control loop
    end_time = datetime.datetime.now()
    control_loop_time = (end_time - start).total_seconds()
    print('This control loop has taken {} min'.format(control_loop_time/60))
    # if the optimization takes reasonable time; continue the process
    i = i + 1
    print('Sleeping {0} seconds...'.format(10))
    time.sleep(10)

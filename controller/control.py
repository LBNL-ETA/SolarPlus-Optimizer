# -*- coding: utf-8 -*-
"""
This script runs the MPC controller in real time.

Since it relies on data manager that gives data at 5 minute intervals,
it can only be run at xx:x5:00 successfully.

"""
islanding = False

import os
import datetime
import time
import pandas as pd
if islanding:
    import mpc_island_config as mpc_config
    from mpc_island_config import tz_computer
else:
    import mpc_config as mpc_config
    from mpc_config import tz_computer
from mpc import mpc

def run():
    # Setup
    # ==============================================================================
    controller = 'mpc'
    start = datetime.datetime.now()
    start_time = start.strftime("%Y-%m-%d %H:%M:00")
    start_time_utc = pd.to_datetime(start_time).tz_localize(tz_computer).tz_convert('UTC')
    #mpc_horizon = 24*3600
    mpc_horizon = 6*3600
    # mpc_step = 3600
    print('\n%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%')
    print("The Solar+ Optimizer has begun its operation at {0} UTC...".format(start_time_utc))
    print("The prediction horizon is {} hours.".format(mpc_horizon/3600))
    print('\n')

    # Initialize
    # ==============================================================================
    # Create output folder under the current directory
    outdir = os.path.abspath(os.path.join(__file__,'..','output'))
    if not os.path.exists(outdir):
        os.mkdir(outdir)

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
    control, measurements, other_outputs, statistics = controller.optimize(start_time_utc, final_time_utc)
    # Save optimization result data
    control.to_csv(outdir+'/control_{0}.csv'.format(start_time))
    measurements.to_csv(outdir+'/measurements_{0}.csv'.format(start_time))
    other_outputs.to_csv(outdir+'/other_outputs_{0}.csv'.format(start_time))
    with open(outdir+'/optimal_statistics_{0}.txt'.format(start_time), 'a') as f:
        f.write(str(start_time) + ': ' +  str(statistics) + '\n')
    # Push setpoints
    setpoints = controller.set_setpoints(control, measurements)
    setpoints.to_csv(outdir+'/setpoints_{0}.txt'.format(start_time))
    # check if setpoints have been pushed successefully
    end_time = datetime.datetime.now()
    control_loop_time = (end_time - start).total_seconds()
    print('This control loop has taken {} min'.format(control_loop_time/60))

if __name__ == '__main__':
    minute = -1
    while True:
        time.sleep(1)
        t = datetime.datetime.now()
        print(t)
        if (t.minute in [0,5,10,15,20,25,30,35,40,45,50,55]) and (t.minute != minute):
            minute = t.minute
            try:
                run()
                print('Run ended ok.')
                # time.sleep(300)
            except Exception as e :
               print('Run ended in error')

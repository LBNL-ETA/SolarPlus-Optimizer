# -*- coding: utf-8 -*-
"""
This script runs the MPC controller in real time.

Since it relies on data manager that gives data at 5 minute intervals,
it can only be run at xx:x5:00 successfully.

"""
import os
import datetime
import time
import pandas as pd
import mpc_config as mpc_config
from mpc_config import tz_computer, islanding
from mpc import mpc

class MPC_Controller:
    def __init__(self, mpc_config, tz_computer, islanding):
        self.mpc_config = mpc_config

        # Initialize
        # ==============================================================================
        # Create output folder under the current directory
        self.outdir = os.path.abspath(os.path.join(__file__,'..','output'))

        self.mpc_horizon = 12*3600
        self.tz_computer = tz_computer
        self.islanding = islanding

        if not os.path.exists(self.outdir):
            os.mkdir(self.outdir)

        #if controller is 'mpc':
        self.config = self.mpc_config.get_config()

    def run(self, start_time_str=None):
        print('\n')
        print('The MPC controller has been instantiated.')
        print('\n')
        controller = mpc(self.config['model_config'],
                              self.config['opt_config'],
                              self.config['system_config'],
                              weather_config=self.config['weather_config'],
                              control_config=self.config['control_config'],
                              setpoints_config=self.config['setpoints_config'],
                              constraint_config=self.config['constraint_config'],
                              data_manager_config=self.config['data_manager_config'],
                              price_config=self.config['price_config'])

        if start_time_str is None:
            start = datetime.datetime.now()
        else:
            start  = datetime.datetime.strptime(start_time_str, "%Y-%m-%d %H:%M:00")

        start_time = start.strftime("%Y-%m-%d %H:%M:00")
        start_time_utc = pd.to_datetime(start_time).tz_localize(self.tz_computer).tz_convert('UTC')
        print('\n%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%')
        print("The Solar+ Optimizer has begun its operation at {0} UTC...".format(start_time_utc))
        print("The prediction horizon is {} hours.".format(self.mpc_horizon/3600))
        if self.islanding:
            print ("Running in islanding mode")
        print('\n')

        final_time_utc = start_time_utc + datetime.timedelta(seconds=self.mpc_horizon)
        control, measurements, other_outputs, statistics = controller.optimize(start_time_utc, final_time_utc)
        # Save optimization result data
        control.to_csv(self.outdir+'/control_{0}.csv'.format(start_time))
        measurements.to_csv(self.outdir+'/measurements_{0}.csv'.format(start_time))
        other_outputs.to_csv(self.outdir+'/other_outputs_{0}.csv'.format(start_time))
        with open(self.outdir+'/optimal_statistics_{0}.txt'.format(start_time), 'a') as f:
            f.write(str(start_time) + ': ' +  str(statistics) + '\n')
        # Push setpoints
        setpoints = controller.set_setpoints(control, measurements)
        setpoints.to_csv(self.outdir+'/setpoints_{0}.txt'.format(start_time))
        # check if setpoints have been pushed successefully
        end_time = datetime.datetime.now()
        control_loop_time = (end_time - start).total_seconds()
        print('This control loop has taken {} min'.format(control_loop_time/60))


if __name__ == '__main__':
    minute = -1
    mpc_controller = MPC_Controller(mpc_config=mpc_config, tz_computer=tz_computer, islanding=islanding)
    while True:
        time.sleep(1)
        t = datetime.datetime.now()
        print(t)
        if (t.minute%5==0) and (t.minute != minute):
            minute = t.minute
            try:
                mpc_controller.run()
                print('Run ended ok.')
            except Exception as e :
                print('Run ended in error, error={0}'.format(str(e)))

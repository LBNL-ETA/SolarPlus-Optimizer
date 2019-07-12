# -*- coding: utf-8 -*-
"""
This module contains unit tests of the MPC controller.

"""
from __future__ import division
import unittest
from controller.mpc import mpc
import tests.mpc_config_testing as mpc_config_testing
import pandas as pd
import pyfunnel as pf
import os
import numpy as np
import shutil
import pytz

config = mpc_config_testing.get_config()

class unit(unittest.TestCase):

    def setUp(self):
        self.tz_local = pytz.timezone("America/Los_Angeles")
        self.tz_utc = pytz.timezone("UTC")
        self.start_time = pd.to_datetime('6/1/2018').tz_localize(self.tz_local).tz_convert(self.tz_utc)
        self.final_time = pd.to_datetime('6/6/2018').tz_localize(self.tz_local).tz_convert(self.tz_utc)
        exo_data = os.path.abspath(os.path.join(__file__,'..','fixtures','exo_data.csv'))
        measurements = os.path.abspath(os.path.join(__file__,'..','fixtures','measurements.csv'))
        state_estimation = os.path.abspath(os.path.join(__file__,'..','fixtures','state_estimation.csv'))
        self.exo_data = pd.read_csv(exo_data,index_col='Time')
        self.measurements = pd.read_csv(measurements,index_col='Time')
        self.state_estimation = pd.read_csv(state_estimation,index_col='Name')
        self.controller = mpc(config['model_config'],
                              config['opt_config'],
                              config['system_config'],
                              weather_config = config['weather_config'],
                              control_config = config['control_config'],
                              setpoints_config = config['setpoints_config'],
                              constraint_config = config['constraint_config'],
                              price_config = config['price_config'],
                              data_manager_config=config['data_manager_config'])

    def test_update_exo(self):
        exo_data = []
        for exo in [self.controller.weather,
                    self.controller.other_input,
                    self.controller.constraint,
                    self.controller.price]:
            self.controller._update_exo(exo, self.start_time, self.final_time)
            if exo:
                exo_data.append(exo.display_data())
        exo_data = pd.concat(exo_data,axis=1)

        # control data has different time index from other exo data
        self.controller._update_exo(self.controller.control, self.start_time, self.final_time)
        control_data = self.controller.control.display_data().resample('5T').mean()
        exo_data = pd.concat([exo_data,control_data],axis=1)

        results_dir = os.path.abspath(os.path.join(__file__,'..','results'))
        for column in exo_data.columns:
            pf.compareAndReport(
                    xReference = pd.to_datetime(self.exo_data.index).astype(np.int64)/1E9,
                    xTest = pd.to_datetime(exo_data.index).astype(np.int64)/1E9,
                    yReference = self.exo_data[column],
                    yTest = exo_data[column],
                    atolx = 1,
                    rtoly = 0.05,
                    outputDirectory = results_dir
                    )
            error_df = pd.read_csv(os.path.join(results_dir, 'errors.csv'))
            self.assertAlmostEqual(error_df.iloc(axis=1)[1].max(),0)
        shutil.rmtree(results_dir)

    def test_update_system(self):
        self.controller._update_system(self.start_time, self.final_time)
        measurements = self.controller.system.display_measurements('Measured')

        results_dir = os.path.abspath(os.path.join(__file__,'..','results'))
        for column in measurements.columns:
            pf.compareAndReport(
                    xReference = pd.to_datetime(self.measurements.index).astype(np.int64)/1E9,
                    xTest = pd.to_datetime(measurements.index).astype(np.int64)/1E9,
                    yReference = self.measurements[column],
                    yTest = measurements[column],
                    atolx = 1,
                    rtoly = 0.05,
                    outputDirectory = results_dir
                    )
            error_df = pd.read_csv(os.path.join(results_dir, 'errors.csv'))
            self.assertAlmostEqual(error_df.iloc(axis=1)[1].max(),0)
        shutil.rmtree(results_dir)

    def test_estimate_state(self):
        self.controller._update_system(self.start_time, self.final_time)
        self.controller._estimate_state(self.final_time)
        state_estimation = self.controller.parameter.display_data()
        self.assertAlmostEqual(self.state_estimation['Value'].sum(),state_estimation['Value'].sum())

if __name__ == '__main__':
    unittest.main()

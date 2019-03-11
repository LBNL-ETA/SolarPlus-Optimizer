# -*- coding: utf-8 -*-
"""
This module contains functional tests of the MPC controller.

"""
from __future__ import division
import unittest
from controller.mpc import mpc
from matplotlib import pyplot as plt
import numpy as np
import tests.mpc_config_testing as mpc_config_testing
import pandas as pd
import os
import sys
import numpy as np
import shutil
import pyfunnel as pf

config = mpc_config_testing.get_config()

class test_simulate(unittest.TestCase):

    def setUp(self):
        # load reference data
        measurements = os.path.abspath(os.path.join(__file__,'..','fixtures','measurements_simulate.csv'))
        other_outputs = os.path.abspath(os.path.join(__file__,'..','fixtures','other_outputs_simulate.csv'))
        self.measurements = pd.read_csv(measurements,index_col='Time')
        self.other_outputs = pd.read_csv(other_outputs,index_col='Time')

    def test_simulate(self):
        start_time = pd.to_datetime('6/1/2018')
        final_time = pd.to_datetime('6/6/2018')
        # Instantiate
        config['model_config']['modelpath'] = 'SolarPlus.Building.Optimization.StoreSim'
        self.controller = mpc(config['model_config'],
                              config['opt_config'],
                              config['system_config'],
                              weather_config = config['weather_config'],
                              control_config = config['control_config'],
                              setpoints_config = config['setpoints_config'],
                              constraint_config = config['constraint_config'],
                              price_config = config['price_config'],
                              data_manager_config=config['data_manager_config'])
        # Simulate
        measurements, other_outputs = self.controller.simulate(start_time, final_time)
        # only measurements results are compared
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

        # Plot
        plt.figure(1)
        for key in measurements.columns:
            plt.plot(measurements.index, measurements[key].get_values()-273.15, label = '{0}_simulated'.format(key), alpha=0.5)
            plt.plot(self.controller.system.display_measurements('Measured').index, self.controller.system.display_measurements('Measured')[key].get_values(), label = '{0}_measured'.format(key), alpha=0.5)
        plt.legend()
        plt.figure(2)
        self.controller.control.display_data().plot()
        plt.show()

class test_optimize(unittest.TestCase):
    def setUp(self):
        # load reference data
        control = os.path.abspath(os.path.join(__file__,'..','fixtures','control_optimize.csv'))
        measurements = os.path.abspath(os.path.join(__file__,'..','fixtures','measurements_optimize.csv'))
        other_outputs = os.path.abspath(os.path.join(__file__,'..','fixtures','other_outputs_optimize.csv'))
        self.control = pd.read_csv(control,index_col='Time')
        self.measurements = pd.read_csv(measurements,index_col='Time')
        self.other_outputs = pd.read_csv(other_outputs,index_col='Time')

    def test_optimize(self):
        start_time = pd.to_datetime('6/1/2018')
        final_time = pd.to_datetime('6/2/2018')
        # Instantiate
        self.controller = mpc(config['model_config'],
                              config['opt_config'],
                              config['system_config'],
                              weather_config = config['weather_config'],
                              control_config = config['control_config'],
                              setpoints_config = config['setpoints_config'],
                              constraint_config = config['constraint_config'],
                              price_config = config['price_config'],
                              data_manager_config=config['data_manager_config'])
        # Optimize
        control, measurements, other_outputs, statistics = self.controller.optimize(start_time, final_time, init=True)

        results_dir = os.path.abspath(os.path.join(__file__,'..','results'))
        for column in control.columns:
            pf.compareAndReport(
                    xReference = pd.to_datetime(self.control.index).astype(np.int64)/1E9,
                    xTest = pd.to_datetime(control.index).astype(np.int64)/1E9,
                    yReference = self.control[column],
                    yTest = control[column],
                    atolx = 1,
                    rtoly = 0.05,
                    outputDirectory = results_dir)
            error_df = pd.read_csv(os.path.join(results_dir, 'errors.csv'))
            self.assertAlmostEqual(error_df.iloc(axis=1)[1].max(),0)
        shutil.rmtree(results_dir)

        # Plot
        for key in measurements.columns:
            plt.figure(1)
            time_diff = (measurements.index.values-measurements.index.values[0])
            time = time_diff/(time_diff[-1])*24
            data = measurements[key].get_values()-273.15
            plt.plot(time, data, label=key)
            plt.legend()
            plt.xlim([0,24])
            plt.xticks(np.linspace(0, 24, num=13))
        plt.savefig('measurements.png')
        for key in control.columns:
            plt.figure(2)
            time_diff = (control.index.values-control.index.values[0])
            time = time_diff/(time_diff[-1])*24
            data = control[key].get_values()
            plt.plot(time, data, label=key)
            plt.legend()
            plt.xlim([0,24])
            plt.xticks(np.linspace(0, 24, num=13))
        plt.savefig('control.png')
        for key in other_outputs.columns:
            if key is 'SOC':
                plt.figure(4)
                time_diff = (other_outputs.index.values-other_outputs.index.values[0])
                time = time_diff/(time_diff[-1])*24
                data = other_outputs[key].get_values()
                plt.plot(time, data, label=key)
                plt.legend()
                plt.xlim([0,24])
                plt.ylim([0,0.5])
                plt.xticks(np.linspace(0, 24, num=13))
                plt.savefig('SOC.png')
            else:
                plt.figure(3)
                time_diff = (other_outputs.index.values-other_outputs.index.values[0])
                time = time_diff/(time_diff[-1])*24
                data = other_outputs[key].get_values()
                plt.plot(time, data, label=key)
                plt.legend()
                plt.xlim([0,24])
                plt.ylim([-15000,25000])
                plt.xticks(np.linspace(0, 24, num=13))
                plt.savefig('Power.png')
        for key in self.controller.price.display_data().columns:
            plt.figure(5)
            time_diff = (self.controller.price.display_data().index.values-self.controller.price.display_data().index.values[0])
            time = time_diff/(time_diff[-1])*24
            data = self.controller.price.display_data()[key].get_values()
            plt.plot(time, data, label=key)
            plt.legend()
            plt.xlim([0,24])
            plt.xticks(np.linspace(0, 24, num=13))
            plt.savefig('price.png')
        plt.show()

if __name__ == '__main__':
    unittest.main()

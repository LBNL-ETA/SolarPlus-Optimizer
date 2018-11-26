# -*- coding: utf-8 -*-
"""
This module contains unit tests of the MPC controller.

"""
import unittest
from mpc import mpc
from matplotlib import pyplot as plt
import numpy as np
import mpc_config
import pandas as pd

config = mpc_config.get_config()
                             
class unit(unittest.TestCase):
    
    def setUp(self):
        self.start_time = pd.to_datetime('6/1/2018')
        self.final_time = pd.to_datetime('6/6/2018')
        self.controller = mpc(config['model_config'],
                              config['opt_config'], 
                              config['system_config'],
                              weather_config = config['weather_config'],
                              control_config = config['control_config'],
                              constraint_config = config['constraint_config'],
                              price_config = config['price_config'])
    
    def test_update_exo(self):
        for exo in [self.controller.weather, 
                    self.controller.control, 
                    self.controller.other_input, 
                    self.controller.constraint, 
                    self.controller.price]:
            self.controller._update_exo(exo, self.start_time, self.final_time)
            if exo:
                print(exo.display_data())
    
    def test_update_system(self):
        self.controller._update_system(self.start_time, self.final_time)
        print(self.controller.system.display_measurements('Measured'))
        
    def test_estimate_state(self):
        self.controller._update_system(self.start_time, self.final_time)
        self.controller._estimate_state(self.final_time)
        print(self.controller.parameter.display_data())
        
class functional(unittest.TestCase):
    
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
                              constraint_config = config['constraint_config'],
                              price_config = config['price_config'])
        # Simulate
        measurements, other_outputs = self.controller.simulate(start_time, final_time)
        # Plot
        plt.figure(1)
        for key in measurements.columns:
            plt.plot(measurements.index, measurements[key].get_values()-273.15, label = '{0}_simulated'.format(key), alpha=0.5)
            plt.plot(self.controller.system.display_measurements('Measured').index, self.controller.system.display_measurements('Measured')[key].get_values(), label = '{0}_measured'.format(key), alpha=0.5) 
        plt.legend()
        plt.figure(2)
        self.controller.control.display_data().plot()
        plt.show()
        
    def test_optimize(self):
        start_time = pd.to_datetime('6/1/2018')
        final_time = pd.to_datetime('6/2/2018')
        # Instantiate
        self.controller = mpc(config['model_config'],
                              config['opt_config'], 
                              config['system_config'],
                              weather_config = config['weather_config'],
                              control_config = config['control_config'],
                              constraint_config = config['constraint_config'],
                              price_config = config['price_config'])
        # Optimize
        control, measurements, other_outputs, statistics = self.controller.optimize(start_time, final_time, init=True)
        
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
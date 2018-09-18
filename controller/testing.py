# -*- coding: utf-8 -*-
"""
This module contains unit tests of the MPC controller.

"""
from mpcpy import units
import unittest
from mpc import mpc
import os
from matplotlib import pyplot as plt

model_config =      {'mopath' : os.path.join('models','SolarPlus.mo'),
                     'modelpath' : 'SolarPlus.Building.Optimization.Store',
                     'libraries' : os.getenv('MODELICAPATH'),
                     'measurements' : ['Trtu', 'Tref', 'Tfre'],
                     'sample_rate' : 3600,
                     'parameters' : {'Name':      ['Trtu_0', 'Tref_0', 'Tfre_0', 'SOC_0'], 
                                     'Free':      [False,    False,    False,    False],
                                     'Value':     [0,        0,        0,        0.5],
                                     'Minimum':   [10,       0,        -40,      0],
                                     'Maximum':   [35,       20,       0,        1],
                                     'Covariance':[0,        0,        0,        0],
                                     'Unit' :     ['degC',   'degC',   'degC',   '1']},
                      'init_vm' : {'Trtu_0' : 'Trtu',
                                   'Tref_0' : 'Tref',
                                   'Tfre_0' : 'Tfre'}}

opt_config =        {'problem'  : 'EnergyMin',
                     'power_var': 'J'} 

weather_config =    {'type': 'csv',
                     'path': os.path.join('data','Temperature.csv'),
                     'vm'  : {'Outdoor':('weaTDryBul', units.degC),
                              'Solar Radiation':('weaHGloHor', units.W_m2)},
                     'geo' : (40.88,-124.0)}
                               
control_config =    {'type': 'csv',
                     'path': os.path.join('data','Control2.csv'),
                     'vm'  : {'HVAC1_Norm' : ('uCool', units.unit1),
                              'RefComp_Norm' : ('uRef', units.unit1),
                              'FreComp_Split_Norm' : ('uFreCool', units.unit1),
                              'uHeat' : ('uHeat', units.unit1),
                              'uCharge' : ('uCharge', units.unit1),
                              'uDischarge' : ('uDischarge', units.unit1)}}
                               
constraint_config = {'type': 'csv',
                     'path': os.path.join('data','Constraint.csv'),
                     'vm'  : {'Trtu_min':('Trtu', 'GTE', units.degC),
                              'Trtu_max':('Trtu', 'LTE', units.degC),
                              'Tref_min':('Tref', 'GTE', units.degC),
                              'Tref_max':('Tref', 'LTE', units.degC),
                              'Tfre_min':('Tfre', 'GTE', units.degC),
                              'Tfre_max':('Tfre', 'LTE', units.degC),
                              'SOC_min':('SOC', 'GTE', units.unit1),
                              'SOC_max':('SOC', 'LTE', units.unit1),
                              'uCool_min':('uCool', 'GTE', units.unit1),
                              'uCool_max':('uCool', 'LTE', units.unit1),
                              'uHeat_min':('uHeat', 'GTE', units.unit1),
                              'uHeat_max':('uHeat', 'LTE', units.unit1),
                              'uCharge_min':('uCharge', 'GTE', units.unit1),
                              'uCharge_max':('uCharge', 'LTE', units.unit1),
                              'uDischarge_min':('uDischarge', 'GTE', units.unit1),
                              'uDischarge_max':('uDischarge', 'LTE', units.unit1),
                              'uRef_min':('uRef', 'GTE', units.unit1),
                              'uRef_max':('uRef', 'LTE', units.unit1),
                              'uFreCool_min':('uFreCool', 'GTE', units.unit1),
                              'uFreCool_max':('uFreCool', 'LTE', units.unit1)}}
                              
price_config =      {'type': 'csv',
                     'path': os.path.join('data','Price.csv'),
                     'vm'  : {'pi_e':('pi_e', units.dol_kWh)}}

system_config =     {'type': 'csv',
                     'path': os.path.join('data','Temperature.csv'),
                     'vm'  : {'Refrigerator East':('Tref', units.degC),
                              'HVAC East':('Trtu', units.degC),
                              'Freezer':('Tfre', units.degC)}}
                             
class unit(unittest.TestCase):
    
    def setUp(self):
        self.start_time = '6/1/2018'
        self.final_time = '6/6/2018'
        self.controller = mpc(model_config, opt_config, system_config,
                              weather_config = weather_config,
                              control_config = control_config,
                              constraint_config = constraint_config,
                              price_config = price_config)
    
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
        # Instantiate
        model_config['modelpath'] = 'SolarPlus.Building.Optimization.StoreSim'
        self.controller = mpc(model_config, opt_config, system_config,
                              weather_config = weather_config,
                              control_config = control_config,
                              constraint_config = constraint_config,
                              price_config = price_config)
        # Simulate
        solution = self.controller.simulate('6/1/2018', '6/6/2018')
        # Plot
        plt.figure(1)
        for key in solution.columns:
            plt.plot(solution.index, solution[key].get_values()-273.15, label = '{0}_simulated'.format(key), alpha=0.5)
            plt.plot(self.controller.system.display_measurements('Measured').index, self.controller.system.display_measurements('Measured')[key].get_values(), label = '{0}_measured'.format(key), alpha=0.5) 
        plt.legend()
        plt.figure(2)
        self.controller.control.display_data().plot()
        plt.show()
        
    def test_optimize(self):
        # Instantiate
        self.controller = mpc(model_config, opt_config, system_config,
                              weather_config = weather_config,
                              control_config = control_config,
                              constraint_config = constraint_config,
                              price_config = price_config)
        # Optimize
        control, measurements, statistics = self.controller.optimize('6/1/2018', '6/2/2018', init=True)
        # Plot
        plt.figure(1)
        measurements.plot()
        plt.legend()
        plt.figure(2)
        control.plot()
        plt.legend()
        plt.show()
        
            
                         
if __name__ == '__main__':
    unittest.main()
# -*- coding: utf-8 -*-
"""
This module contains unit tests of the MPC controller.

"""
from mpcpy import units
import unittest
from mpc import mpc
import os

model_config =      {'mopath' : os.path.join('models','SolarPlus.mo'),
                             'modelpath' : 'SolarPlus.Building.Whole_Inputs',
                             'libraries' : os.getenv('MODELICAPATH'),
                             'measurements' : ['Trtu', 'Tref', 'Tfre', 
                                               'weaTDryBul', 'SOC', 'Prtu',
                                               'Pref', 'Pfre', 'Pcharge', 
                                               'Pdischarge', 'Pnet', 'Ppv',
                                               'uCharge', 'uDischarge', 
                                               'uHeat', 'uCool', 'uRef', 
                                               'uFreCool'],
                             'sample_rate' : 3600,
                             'parameters' : {'Name':      ['Trtu_0', 'Tref_0', 'Tfre_0', 'SOC_0'], 
                                             'Free':      [False,    False,    False,    False],
                                             'Value':     [0,        0,        0,        0],
                                             'Minimum':   [10,       0,        -40,      0],
                                             'Maximum':   [35,       20,       0,        1],
                                             'Covariance':[0,        0,        0,        0],
                                             'Unit' :     ['degC',   'degC',   'degC',   '1']},
                             'init_vm' : {'Trtu_0' : 'Trtu',
                                          'Tref_0' : 'Tref',
                                          'Tfre_0' : 'Tfre',
                                          'SOC_0'  : 'SOC'}}

opt_config =        {'problem'  : 'EnergyCostMin',
                     'power_var': 'J'} 

weather_config =    {'type': 'csv',
                     'path': os.path.join('data','Temperature.csv'),
                     'vm'  : {'Outdoor':('weaTDryBul', units.degC)},
                     'geo' : (40.88,-124.0)}
                               
control_config =    {'type': 'csv',
                     'path': os.path.join('data','Control.csv'),
                     'vm'  : {'HVAC1_Norm' : ('uCool', units.unit1),
                              'RefComp_Norm' : ('uRef', units.unit1),
                              'FreComp_Split_Norm' : ('uFreCool', units.unit1),
                              'FreHeater_Split_Norm' : ('uFreDef', units.unit1)}}
                               
constraint_config = {'type': 'csv',
                     'path': os.path.join('data','Constraint.csv'),
                     'vm'  : {}}
                     
price_config =      {'type': 'csv',
                     'path': os.path.join('data','Price.csv'),
                     'vm'  : {'pi_e':('pi_e', units.dol_kWh)}}

system_config =     {'type': 'csv',
                     'path': os.path.join('data','System.csv'),
                     'vm'  : {}}
                             
class instantiate(unittest.TestCase):
    
    def test_instantiate(self):
        
        controller = mpc(model_config, opt_config, system_config,
                         weather_config = weather_config,
                         control_config = control_config,
                         constraint_config = constraint_config,
                         price_config = price_config)
                         
if __name__ == '__main__':
    unittest.main()
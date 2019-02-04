# -*- coding: utf-8 -*-
"""
Created on Mon Oct 22 09:28:55 2018

@author: dhb-lx
"""

from mpcpy import units
import os

config={"model_config" :{'mopath' : os.path.join('models','SolarPlus.mo'),
                         'modelpath' : 'SolarPlus.Building.Optimization.Store',
                         'libraries' : os.getenv('MODELICAPATH'),
                         'measurements' : ['Trtu', 'Tref', 'Tfre'],
                         'other_outputs' : ['Pnet', 'Prtu', 'Pref', 'Pfre','Pcharge', 'Pdischarge', 'SOC'],
                         'sample_rate' : 3600,
                         'parameters' : {'Name':      ['Trtu_0', 'Tref_0', 'Tfre_0', 'SOC_0'],
                                         'Free':      [False,    False,    False,    False],
                                         'Value':     [0,        0,        0,        0.25],
                                         'Minimum':   [10,       0,        -40,      0],
                                         'Maximum':   [35,       20,       0,        1],
                                         'Covariance':[0,        0,        0,        0],
                                         'Unit' :     ['degC',   'degC',   'degC',   '1']},
                          'init_vm' : {'Trtu_0' : 'Trtu',
                                       'Tref_0' : 'Tref',
                                       'Tfre_0' : 'Tfre'}},

"opt_config" :        {'problem'  : 'EnergyCostMin',
                     'power_var': 'J'},

"weather_config" :    {'type': 'csv',
                     'path': os.path.join('data','Temperature.csv'),
                     'vm'  : {'Outdoor':('weaTDryBul', units.degC),
                              'Solar Radiation':('weaHGloHor', units.W_m2)},
                     'geo' : (40.88,-124.0)},

"control_config" :    {'type': 'csv',
                     'path': os.path.join('data','Control2.csv'),
                     'vm'  : {
                              # new columns from csv required for the following values
                              'FreComp': ('FreComp', units.kW),
                              'RefComp': ('RefComp', units.kW),
                              'HVAC1': ('HVAC1', units.kW),

                              'HVAC1_Norm' : ('uCool', units.unit1),
                              'RefComp_Norm' : ('uRef', units.unit1),
                              'FreComp_Split_Norm' : ('uFreCool', units.unit1),
                              'uHeat' : ('uHeat', units.unit1),
                              'uCharge' : ('uCharge', units.unit1),
                              'uDischarge' : ('uDischarge', units.unit1)}},

"constraint_config" : {'type': 'csv',
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
                              'uFreCool_max':('uFreCool', 'LTE', units.unit1),
                              'demand':('Pnet', 'LTE', units.kW)}},

"price_config" :      {'type': 'csv',
                     'path': os.path.join('data','Price.csv'),
                     'vm'  : {'pi_e':('pi_e', units.dol_kWh)}},

"system_config" :     {'type': 'csv',
                     'path': os.path.join('data','Temperature.csv'),
                     'vm'  : {'Tref':('Tref', units.K),
                              'Trtu':('Trtu', units.K),
                              'Tfre':('Tfre', units.K),
                              'SOC':('SOC',units.unit1)}},
"csv_files": [
    "Temperature.csv",
    "Price.csv",
    "Control2.csv",
    "Constraint.csv",
    "emulation_states.csv"
    ]
}

def get_config():

    return config

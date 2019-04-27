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

"weather_config" :    {
                     'vm'  : {'Outdoor':('weaTDryBul', units.degC),
                              'Solar Radiation':('weaHGloHor', units.W_m2)},
                     'geo' : (40.88,-124.0)},

"control_config" :    {
                     'vm'  : {
                              'HVAC1_Norm' : ('uCool', units.unit1),
                              'RefComp_Norm' : ('uRef', units.unit1),
                              'FreComp_Split_Norm' : ('uFreCool', units.unit1),
                              'uHeat' : ('uHeat', units.unit1),
                              'uCharge' : ('uCharge', units.unit1),
                              'uDischarge' : ('uDischarge', units.unit1)}},

"constraint_config" : {
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

"price_config" :      {
                     'vm'  : {'pi_e':('pi_e', units.dol_kWh)}},

"system_config" :     {
                     'vm'  : {'Tref':('Tref', units.degC),
                              'Trtu':('Trtu', units.degC),
                              'Tfre':('Tfre', units.degC),
                              # 'SOC':('SOC',units.unit1)
                              }
                       },
"setpoints_config" :   {
                      'vm'  : {'uCharge':('uCharge',units.unit1),
                               'uDischarge':('uDischarge',units.unit1),
                               'Trtu':('Trtu',units.degC),
                               'Tref':('Tref',units.degC),
                               'Tfre':('Tfre',units.degC)
#                              'Trtu_cool':('Trtu',units.degC),
#                               'Trtu_heat':('Trtu',units.degC)
                               }
                        },
"data_manager_config": {
    "source": {
        "csv_files": [
            # "Temperature.csv",
            # "Price.csv",
            # "Control2.csv",
            # "Constraint.csv",
            # "setpoints.csv"
            # "emulation_states.csv",
        ],
        "influxdb": {
            "config_filename": "controller/access_config_testing.yaml",
            "section": "influxdb"
        },
        "xbos": {
            "container_url":'http://datamanager:5000'}
    },
    "weather": {
        # "type": "csv",
        "type": "xbos",
        "measurement": "temperature",
        "variables": {
            "Outdoor": "Outdoor",
            "Solar Radiation": "Solar Radiation"
        }
    },
    "control": {
        # "type": "csv",
        "type": "xbos",
        "measurement": "control",
        "variables": {
            "FreComp": "FreComp",
            "RefComp": "RefComp",
            "HVAC1": "HVAC1"
        }
    },
    "constraint": {
        # "type": "csv",
        "type": "xbos",
        "measurement": "constraint",
        "variables": {
            "Trtu_min": "Trtu_min",
            "Trtu_max": "Trtu_max",
            "Tref_min": "Tref_min",
            "Tref_max": "Tref_max",
            "Tfre_min": "Tfre_min",
            "Tfre_max": "Tfre_max",
            "SOC_min": "SOC_min",
            "SOC_max": "SOC_max",
            "uCool_min": "uCool_min",
            "uCool_max": "uCool_max",
            "uHeat_min": "uHeat_min",
            "uHeat_max": "uHeat_max",
            "uCharge_min": "uCharge_min",
            "uCharge_max": "uCharge_max",
            "uDischarge_min": "uDischarge_min",
            "uDischarge_max": "uDischarge_max",
            "uRef_min": "uRef_min",
            "uRef_max": "uRef_max",
            "uFreCool_min": "uFreCool_min",
            "uFreCool_max": "uFreCool_max",
            "demand": "demand"
        }
    },
    "price": {
        # "type": "csv",
        "type": "xbos",
        "measurement": "price",
        "variables": {
            "pi_e": "pi_e"
        }
    },
    "system": {
        # TODO: change to emulation states measuremnt
        "type": "xbos",
        "measurement": "temperature",
        "variables": {
            "Refrigerator East": "Tref",
            "HVAC East": "Trtu",
            "Freezer": "Tfre",
        }
    },
    "data_sink": {
        "setpoints": {
            # "type": "csv",
            # "filename": "setpoints.csv"
            # "type": "influxdb",
            # "measurement": "setpoints"
            "type": "xbos"
        },
        "variables": {
            "uCharge": {
                "type": "csv",
                "filename": "setpoints.csv"
            },
            "uDischarge": {
                "type": "csv",
                "filename": "setpoints.csv"
            },
            "Trtu": {
                "type": "csv",
                "filename": "setpoints.csv"
            },
            "Tref": {
                "type": "csv",
                "filename": "setpoints.csv"
            },
            "Tfre": {
                "type": "csv",
                "filename": "setpoints.csv"
            },
            "Trtu_cool": {
                "type": "csv",
                "filename": "setpoints.csv"
            },
            "Trtu_heat": {
                "type": "csv",
                "filename": "setpoints.csv"
            }
        }

    }
},
"plot_charts": False
}

def get_config():

    return config

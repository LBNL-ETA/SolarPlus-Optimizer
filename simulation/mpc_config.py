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
                         'measurements' : ['Trtu', 'Tref', 'Tfre', 'SOC'],
                         'other_outputs' : ['Pnet', 'Prtu', 'Pref', 'Pfre','Pbattery', 'Grtu'],
                         'sample_rate' : 1800,
                         'parameters' : {'Name':      ['Trtu_0', 'Tref_0', 'Tfre_0', 'SOC_0'],
                                         'Free':      [False,    False,    False,    False],
                                         'Value':     [294.15,   276.65,   248.15,     0.5],
                                         'Minimum':   [283.15,   273.15,   233.15,      0],
                                         'Maximum':   [308.15,   293.15,   273.15,      1],
                                         'Covariance':[0,        0,        0,        0],
                                         'Unit' :     ['K',   'K',   'K',   '1']},
                          'init_vm' : {'Trtu_0' : 'Trtu',
                                       'Tref_0' : 'Tref',
                                       'Tfre_0' : 'Tfre',
                                       'SOC_0' : 'SOC'}},

"opt_config" :        {'problem'  : 'EnergyCostMin',
                     'power_var': 'J'},

"weather_config" :    {
                     'vm'  : {'Outdoor':('weaTDryBul', units.degC),
                              'Solar Radiation':('weaHGloHor', units.W_m2)},
                     'geo' : (40.88,-124.0)},

"control_config" :    {
                     'vm'  : {
                              # new columns from csv required for the following values
                              'FreComp': ('FreComp', units.kW),
                              'RefComp': ('FreComp', units.kW),
                              'HVAC1': ('FreComp', units.kW),

                              'HVAC1_Norm' : ('uCool', units.unit1),
                              'RefComp_Norm' : ('uRef', units.unit1),
                              'FreComp_Split_Norm' : ('uFreCool', units.unit1),
                              'uHeat' : ('uHeat', units.unit1),
                              'uBattery' : ('uBattery', units.unit1)}},
                              #'uDischarge' : ('uDischarge', units.unit1)}},

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
                              'uBattery_min':('uBattery', 'GTE', units.unit1),
                              'uBattery_max':('uBattery', 'LTE', units.unit1),
                              #'uDischarge_min':('uDischarge', 'GTE', units.unit1),
                              #'uDischarge_max':('uDischarge', 'LTE', units.unit1),
                              'uRef_min':('uRef', 'GTE', units.unit1),
                              'uRef_max':('uRef', 'LTE', units.unit1),
                              'uFreCool_min':('uFreCool', 'GTE', units.unit1),
                              'uFreCool_max':('uFreCool', 'LTE', units.unit1),
                              'demand':('Pnet', 'LTE', units.kW)}},

"price_config" :      {
                     'vm'  : {'pi_e':('pi_e', units.dol_kWh)}},

"system_config" :     {
                     'vm'  : {'Tref':('Tref', units.K),
                              'Trtu':('Trtu', units.K),
                              'Tfre':('Tfre', units.K),
                              'SOC':('SOC',units.unit1)}},

"setpoints_config" :   {
                      'vm'  : {'uBattery':('uBattery',units.unit1),
                               #'uDischarge':('uDischarge',units.unit1),
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
            "Constraint.csv",
            "Control2.csv",
            "Price.csv",
            #"setpoints.csv",
            #"Temperature.csv",
            "emulation_states.csv",
        ],
        "influxdb": {
            "config_filename": "controller/access_config_testing.yaml",
            "section": "influxdb"
        }
    },
    "weather": {
        # type": "csv",
        "type": "influxdb",
        "measurement": "temperature",
        "variables": {
            "Outdoor": "Outdoor",
            "Solar Radiation": "Solar Radiation"
        }
    },
    "control": {
        "type": "csv",
        #"type": "influxdb",
        "measurement": "control",
        "variables": {
            "FreComp": "FreComp",
            "RefComp": "RefComp",
            "HVAC1": "HVAC1"
        }
    },
    "constraint": {
        "type": "csv",
        # "type": "influxdb",
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
            "uBattery_min": "uBattery_min",
            "uBattery_max": "uBattery_max",
            #"uDischarge_min": "uDischarge_min",
            #"uDischarge_max": "uDischarge_max",
            "uRef_min": "uRef_min",
            "uRef_max": "uRef_max",
            "uFreCool_min": "uFreCool_min",
            "uFreCool_max": "uFreCool_max",
            "demand": "demand"
        }
    },
    "price": {
        "type": "csv",
        #"type": "influxdb",
        "measurement": "price",
        "variables": {
            "pi_e": "pi_e"
        }
    },
    "system": {
        "type": "csv",
        "variables": {
            "Tref": "Tref",
            "Trtu": "Trtu",
            "Tfre": "Tfre",
            "SOC": "SOC"
            # "Refrigerator East": "Tref",
            # "HVAC East": "Trtu",
            # "Freezer": "Tfre",
        }
    },
    "setpoints": {
        #"type": "csv",
        "type": "influxdb",
        "measurement": "setpoints",
        "variables": {
            'Trtu_heat': 'Trtu_heat',
            'Trtu_cool': 'Trtu_cool',
            'Tref': 'Tref',
            'Tfre': 'Tfre',
            'uBattery': 'uBattery',
            #'uDischarge': 'uDischarge'
        }
    },
    "data_sink": {
        "setpoints": {
            #"type": "csv",
            "type": "csv|influxdb",
            "measurement": "setpoints",
            "filename": "setpoints.csv"
        },
        "variables": {
            "uBattery": {
                "type": "csv",
                "filename": "setpoints.csv"
            },
            #"uDischarge": {
            #    "type": "csv",
            #    "filename": "setpoints.csv"
            #},
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
"use_data_manager_in_emulator": True
}

def get_config():

    return config

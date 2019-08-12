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
                         'measurements' : ['Trtu', 'Tref', 'Tfre', 'SOC', 'Pbattery'],
                         'other_outputs' : ['Pnet', 'Prtu', 'Pref', 'Pfre', 'Pbattery', 'Grtu'],
                         'sample_rate' : 3600,
                         'parameters' : {'Name':      ['Trtu_0', 'Tref_0', 'Tfre_0', 'SOC_0'],
                                         'Free':      [False,    False,    False,    False],
                                         'Value':     [295.15,   276.65,   248.15,     0.5],
                                         'Minimum':   [283.15,   273.15,   233.15,      0],
                                         'Maximum':   [308.15,   293.15,   273.15,      1],
                                         'Covariance':[0,        0,        0,        0],
                                         'Unit' :     ['K',   'K',   'K',   '1']},
                          'init_vm' : {'Trtu_0' : 'Trtu',
                                       'Tref_0' : 'Tref',
                                       'Tfre_0' : 'Tfre',
                                       'SOC_0'  : 'SOC'}},

"opt_config" :        {'problem'  : 'EnergyCostMin',
                     'power_var': 'J'},

"weather_config" :    {'type': 'csv',
                     'path': os.path.join('data','Temperature.csv'),
                     'vm'  : {'Outdoor':('weaTDryBul', units.degC),
                              'poa_pv':('weaPoaPv', units.W_m2),
                              'poa_win': ('weaPoaWin', units.W_m2)},
                     'geo' : (40.88,-124.0)},

"control_config" :    {'type': 'csv',
                     'path': os.path.join('data','Control2.csv'),
                     'vm'  : {
                              'HVAC1_Norm' : ('uCool', units.unit1),
                              'RefComp_Norm' : ('uRef', units.unit1),
                              'FreComp_Split_Norm' : ('uFreCool', units.unit1),
                              'uHeat' : ('uHeat', units.unit1),
                              'uBattery' : ('uBattery', units.unit1)}},

"constraint_config" : {'type': 'csv',
                     'path': os.path.join('data','Constraint.csv'),
                     'vm'  : {
                              # 'Trtu_min':('Trtu', 'GTE', units.degC),
                              # 'Trtu_max':('Trtu', 'LTE', units.degC),
                              # 'Tref_min':('Tref', 'GTE', units.degC),
                              # 'Tref_max':('Tref', 'LTE', units.degC),
                              # 'Tfre_min':('Tfre', 'GTE', units.degC),
                              # 'Tfre_max':('Tfre', 'LTE', units.degC),
                              'SOC_min':('SOC', 'GTE', units.unit1),
                              'SOC_max':('SOC', 'LTE', units.unit1),
                              'uCool_min':('uCool', 'GTE', units.unit1),
                              'uCool_max':('uCool', 'LTE', units.unit1),
                              'uHeat_min':('uHeat', 'GTE', units.unit1),
                              'uHeat_max':('uHeat', 'LTE', units.unit1),
                              'uBattery_min':('uBattery', 'GTE', units.unit1),
                              'uBattery_max':('uBattery', 'LTE', units.unit1),
                              'uRef_min':('uRef', 'GTE', units.unit1),
                              'uRef_max':('uRef', 'LTE', units.unit1),
                              'uFreCool_min':('uFreCool', 'GTE', units.unit1),
                              'uFreCool_max':('uFreCool', 'LTE', units.unit1),
                              'Pmin': ('Pnet', 'GTE', units.kW),
                              'Pmax': ('Pnet', 'LTE', units.kW)
                              }
                              },

"price_config" :      {'type': 'csv',
                     'path': os.path.join('data','Price.csv'),
                     'vm'  : {'pi_e':('pi_e', units.dol_kWh),
                              'pi_d':('pi_d', units.dol_kW),
                              'P_est':('P_est', units.kW)}},

"system_config" :     {'type': 'csv',
                     'path': os.path.join('data','emulation_states.csv'),
                     'vm'  : {'Tref':('Tref', units.degC),
                              'Trtu':('Trtu', units.degC),
                              'Tfre':('Tfre', units.degC),
                              'SOC':('SOC',units.unit1)
                              }
                       },
"setpoints_config" :   {
                      'vm': {'uBattery':('uBattery',units.unit1),
                             'Pbattery':('Pbattery',units.W),
                             'Trtu':('Trtu',units.degC),
                             'Tref':('Tref',units.degC),
                             'Tfre':('Tfre',units.degC),
                             'Trtu_cool':('Trtu',units.degC),
                             'Trtu_heat':('Trtu',units.degC)
                               }
                        },
"data_manager_config": {
    "site": "blr",
    "source": {
        "csv_files": [
            "Temperature.csv",
            "Price.csv",
            "Control2.csv",
            "Constraint.csv",
            # "setpoints.csv",
            "emulation_states.csv"
        ]
    },
    "weather": {
        "type": "csv",
        # "type": "influxdb",
        "variables": {
            # influxdb/xbos
            # "Outdoor": {"uuid": "86f72439-35a3-4997-a14f-24f8a889b164", "window": "5m", "agg": "mean", "measurement": "timeseries"},
            # "Solar Radiation": {"uuid": "cbe9c24e-f8ab-41d5-be16-3ecb5b441a39", "window": "5m", "agg": "mean", "measurement": "timeseries"}

            # csv
            "Outdoor": {"filename": "Temperature.csv", "column": "Outdoor", "tz":"America/Los_Angeles", "agg": "mean", "window": "5m"},
            "poa_pv": {"filename": "Temperature.csv", "column": "poa_pv", "tz":"America/Los_Angeles", "agg": "mean", "window": "5m"},
            "poa_win": {"filename": "Temperature.csv", "column": "poa_win", "tz":"America/Los_Angeles", "agg": "mean", "window": "5m"}
        }
    },
    "control": {
        "type": "csv",
        "variables": {
            "FreComp": {"filename": "Control2.csv", "column": "FreComp", "tz":"America/Los_Angeles", "agg": "mean", "window": "5m"},
            "RefComp": {"filename": "Control2.csv", "column": "RefComp", "tz":"America/Los_Angeles", "agg": "mean", "window": "5m"},
            "HVAC1": {"filename": "Control2.csv", "column": "HVAC1", "tz":"America/Los_Angeles", "agg": "mean", "window": "5m"}
        }
    },
    "constraint": {
        "type": "csv",
        "variables": {
            # "Trtu_min":  {"filename": "Constraint.csv", "column": "Trtu_min", "tz":"America/Los_Angeles", "agg": "mean", "window": "5m"},
            # "Trtu_max":  {"filename": "Constraint.csv", "column": "Trtu_max", "tz":"America/Los_Angeles", "agg": "mean", "window": "5m"},
            # "Tref_min":  {"filename": "Constraint.csv", "column": "Tref_min", "tz":"America/Los_Angeles", "agg": "mean", "window": "5m"},
            # "Tref_max":  {"filename": "Constraint.csv", "column": "Tref_max", "tz":"America/Los_Angeles", "agg": "mean", "window": "5m"},
            # "Tfre_min":  {"filename": "Constraint.csv", "column": "Tfre_min", "tz":"America/Los_Angeles", "agg": "mean", "window": "5m"},
            # "Tfre_max":  {"filename": "Constraint.csv", "column": "Tfre_max", "tz":"America/Los_Angeles", "agg": "mean", "window": "5m"},
            "SOC_min":  {"filename": "Constraint.csv", "column": "SOC_min", "tz":"America/Los_Angeles", "agg": "mean", "window": "5m"},
            "SOC_max":  {"filename": "Constraint.csv", "column": "SOC_max", "tz":"America/Los_Angeles", "agg": "mean", "window": "5m"},
            "uCool_min":  {"filename": "Constraint.csv", "column": "uCool_min", "tz":"America/Los_Angeles", "agg": "mean", "window": "5m"},
            "uCool_max":  {"filename": "Constraint.csv", "column": "uCool_max", "tz":"America/Los_Angeles", "agg": "mean", "window": "5m"},
            "uHeat_min":  {"filename": "Constraint.csv", "column": "uHeat_min", "tz":"America/Los_Angeles", "agg": "mean", "window": "5m"},
            "uHeat_max":  {"filename": "Constraint.csv", "column": "uHeat_max", "tz":"America/Los_Angeles", "agg": "mean", "window": "5m"},
            "uBattery_min":  {"filename": "Constraint.csv", "column": "uBattery_min", "tz":"America/Los_Angeles", "agg": "mean", "window": "5m"},
            "uBattery_max":  {"filename": "Constraint.csv", "column": "uBattery_max", "tz":"America/Los_Angeles", "agg": "mean", "window": "5m"},
            "uRef_min":  {"filename": "Constraint.csv", "column": "uRef_min", "tz":"America/Los_Angeles", "agg": "mean", "window": "5m"},
            "uRef_max":  {"filename": "Constraint.csv", "column": "uRef_max", "tz":"America/Los_Angeles", "agg": "mean", "window": "5m"},
            "uFreCool_min":  {"filename": "Constraint.csv", "column": "uFreCool_min", "tz":"America/Los_Angeles", "agg": "mean", "window": "5m"},
            "uFreCool_max":  {"filename": "Constraint.csv", "column": "uFreCool_max", "tz":"America/Los_Angeles", "agg": "mean", "window": "5m"},
            "Pmin":  {"filename": "Constraint.csv", "column": "Pmin", "tz":"America/Los_Angeles", "agg": "mean", "window": "5m"},
            "Pmax":  {"filename": "Constraint.csv", "column": "Pmax", "tz":"America/Los_Angeles", "agg": "mean", "window": "5m"}
        }
    },
    "price": {
        "type": "csv",
        "variables": {
            "pi_e":  {"filename": "Price.csv", "column": "pi_e", "tz":"America/Los_Angeles", "agg": "mean", "window": "5m"},
            "pi_d":  {"filename": "Price.csv", "column": "pi_d", "tz":"America/Los_Angeles", "agg": "mean", "window": "5m"},
            "P_est":  {"filename": "Price.csv", "column": "P_est", "tz":"America/Los_Angeles", "agg": "mean", "window": "5m"}
        }
    },
    "system": {
        "type": "csv",
        "variables": {
            "Tref": {"filename": "emulation_states.csv", "column": "Tref", "tz":"UTC", "agg": "mean", "window": "5m"},
            "Trtu": {"filename": "emulation_states.csv", "column": "Trtu", "tz":"UTC", "agg": "mean", "window": "5m"},
            "Tfre": {"filename": "emulation_states.csv", "column": "Tfre", "tz":"UTC", "agg": "mean", "window": "5m"},
            "SOC": {"filename": "emulation_states.csv", "column": "SOC", "tz":"UTC", "agg": "mean", "window": "5m"}
        }
    },

    "setpoints": {
        "type": "csv",
        "variables": {
            "Trtu_heat": {"filename": "setpoints.csv", "column": "Trtu_heat", "tz":"UTC", "agg": "mean", "window": "5m"},
            "Trtu_cool": {"filename": "setpoints.csv", "column": "Trtu_cool", "tz":"UTC", "agg": "mean", "window": "5m"},
            "Tref": {"filename": "setpoints.csv", "column": "Tref", "tz":"UTC", "agg": "mean", "window": "5m"},
            "Tfre": {"filename": "setpoints.csv", "column": "Tfre", "tz":"UTC", "agg": "mean", "window": "5m"},
            "uBattery": {"filename": "setpoints.csv", "column": "uBattery", "tz":"UTC", "agg": "mean", "window": "5m"},
            "Pbattery": {"filename": "setpoints.csv", "column": "Pbattery", "tz":"UTC", "agg": "mean", "window": "5m"}
        }
    },

    "data_sink": {
        "setpoints": {
            "type": "csv",
            "filename": "setpoints.csv"
        },
        "variables": {
            "Pbattery": {
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
}
}

def get_config():

    return config

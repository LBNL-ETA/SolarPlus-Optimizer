# -*- coding: utf-8 -*-

from mpcpy import units
import os

config={"model_config" :{'mopath' : os.path.join('models','SolarPlus.mo'),
                         'modelpath' : 'SolarPlus.Building.Optimization.Store',
                         'libraries' : os.getenv('MODELICAPATH'),
                         'measurements' : ['Trtu_west', 'Trtu_east', 'Tref', 'Tfre', 'SOC', 'Pbattery'],
                         'other_outputs' : ['Pnet', 'Prtu_west', 'Prtu_east', 'Pref', 'Pfre', 'Pbattery', 'Ppv', 'Grtu'],
                         'sample_rate' : 3600,
                         'parameters' : {'Name':      ['Trtu_west_0', 'Trtu_east_0', 'Tref_0', 'Tfre_0', 'SOC_0'],
                                         'Free':      [False,   False,    False,    False,    False],
                                         'Value':     [70,       70,      33,        -7,     0.25],
                                         'Minimum':   [0,        0,        0,        -20,      0],
                                         'Maximum':   [100,      100,     50,      100,      1],
                                         'Covariance':[0,        0,        0,        0,      0],
                                         'Unit' :     ['degF',   'degF',   'degF',   'degF', '1']},
                          'init_vm' : {'Trtu_west_0' : 'Trtu_west',
                                       'Trtu_east_0' : 'Trtu_east',
                                       'Tref_0' : 'Tref',
                                       'Tfre_0' : 'Tfre',
                                       'SOC_0'  : 'SOC'}},

"opt_config" :        {'problem'  : 'EnergyPlusDemandCostMin',
                     'power_var': 'J'},

"weather_config" :    {'vm'  : {'Outdoor':('weaTDryBul', units.degF),
                              'poa_pv':('weaPoaPv', units.W_m2),
                              'poa_win': ('weaPoaWin', units.W_m2)},
                     'geo' : (40.88,-124.0)},

"control_config" :    {'vm'  : {
                              'HVAC_West_Norm' : ('uCoolWest', units.unit1),
                              'HVAC_East_Norm' : ('uCoolEast', units.unit1),
                              'RefComp_Norm' : ('uRef', units.unit1),
                              'FreComp_Split_Norm' : ('uFreCool', units.unit1),
                              'uHeat_West' : ('uHeat_West', units.unit1),
                              'uHeat_East' : ('uHeat_East', units.unit1),
                              'uBattery' : ('uBattery', units.unit1)}},

"constraint_config" : {'vm'  : {
#                              'Trtu_min':('Trtu', 'GTE', units.degC),
#                              'Trtu_max':('Trtu', 'LTE', units.degC),
#                              'Tref_min':('Tref', 'GTE', units.degC),
#                              'Tref_max':('Tref', 'LTE', units.degC),
#                              'Tfre_min':('Tfre', 'GTE', units.degC),
#                              'Tfre_max':('Tfre', 'LTE', units.degC),
                              'SOC_min':('SOC', 'GTE', units.unit1),
                              'SOC_max':('SOC', 'LTE', units.unit1),
                              'uCool_min':('uCoolWest', 'GTE', units.unit1),
                              'uCool_max':('uCoolWest', 'LTE', units.unit1),
                              'uHeat_min':('uHeatWest', 'GTE', units.unit1),
                              'uHeat_max':('uHeatWest', 'LTE', units.unit1),
                              'uCool_min':('uCoolEast', 'GTE', units.unit1),
                              'uCool_max':('uCoolEast', 'LTE', units.unit1),
                              'uHeat_min':('uHeatEast', 'GTE', units.unit1),
                              'uHeat_max':('uHeatEast', 'LTE', units.unit1),
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

"price_config" :      {'vm'  : {'pi_e':('pi_e', units.dol_kWh),
                              'pi_d':('pi_d', units.dol_kW),
                              'P_est':('P_est', units.kW)}},

"system_config" :     {'vm'  : {
                                'Trtu_west':('Trtu_west', units.degF),
                                'Trtu_east':('Trtu_east', units.degF),
                                'Tref':('Tref', units.degF),
                                'Tfre':('Tfre', units.degF)
#                              'SOC':('SOC',units.unit1)
                              }
                       },
"setpoints_config" :   {'vm': {'uBattery':('uBattery',units.unit1),
                             'Pbattery':('Pbattery',units.W),
                             'Trtu_west':('Trtu_west',units.degF),
                             'Trtu_east':('Trtu_east',units.degF),
                             'Tref':('Tref',units.degF),
                             'Tfre':('Tfre',units.degF)
                               }
                        },
"data_manager_config": {
    "site": "blr",
    "source": {
        "csv_files": [
            # "Shadow/Weather_Forecast.csv",
            "Shadow/Price_Forecast.csv",
            "Shadow/Constraints_Forecast.csv"
        ],
        "influxdb": {"config_filename":"database_client/config.yaml",
                     "section": "database"}
    },
    "weather": {
        "type": "influxdb",
        "variables": {
            "Outdoor": {"uuid": "69be4db0-48f5-592f-b5a1-e2e695f28ad1", "window": "1m", "agg": "mean", "measurement": "timeseries"},
            "poa_pv": {"uuid": "a8357adb-c59d-5316-a0e8-51d2b2948c75", "window": "1m", "agg": "mean", "measurement": "timeseries"},
            "poa_win": {"uuid": "d1746bb1-7b20-5d20-92b6-60acef287662", "window": "1m", "agg": "mean", "measurement": "timeseries"}
        }
    },
    "control": {
        "type": "csv",
        "variables": {
            "FreComp_Split_Norm": {"filename": "Shadow/Control_InitialGuess.csv", "column": "FreComp_Split_Norm", "tz":"America/Los_Angeles", "agg": "mean", "window": "1m"},
            "RefComp_Norm": {"filename": "Shadow/Control_InitialGuess.csv", "column": "RefComp_Norm", "tz":"America/Los_Angeles", "agg": "mean", "window": "1m"},
            "HVAC_West_Norm": {"filename": "Shadow/Control_InitialGuess.csv", "column": "HVAC_West_Norm", "tz":"America/Los_Angeles", "agg": "mean", "window": "1m"},
            "HVAC_East_Norm": {"filename": "Shadow/Control_InitialGuess.csv", "column": "HVAC_East_Norm", "tz":"America/Los_Angeles", "agg": "mean", "window": "1m"},
            "uHeat_West": {"filename": "Shadow/Control_InitialGuess.csv", "column": "uHeat_West", "tz":"America/Los_Angeles", "agg": "mean", "window": "1m"},
            "uHeat_East": {"filename": "Shadow/Control_InitialGuess.csv", "column": "uHeat_East", "tz":"America/Los_Angeles", "agg": "mean", "window": "1m"},
            "uBattery": {"filename": "Shadow/Control_InitialGuess.csv", "column": "uBattery", "tz":"America/Los_Angeles", "agg": "mean", "window": "1m"}
        }
    },
    "constraint": {
        "type": "csv",
        "variables": {
#            "Trtu_min":  {"filename": "Shadow/Constraint_Forecast.csv", "column": "Trtu_min", "tz":"America/Los_Angeles", "agg": "mean", "window": "5m"},
#            "Trtu_max":  {"filename": "Shadow/Constraint_Forecast.csv", "column": "Trtu_max", "tz":"America/Los_Angeles", "agg": "mean", "window": "5m"},
#            "Tref_min":  {"filename": "Shadow/Constraint_Forecast.csv", "column": "Tref_min", "tz":"America/Los_Angeles", "agg": "mean", "window": "5m"},
#            "Tref_max":  {"filename": "Shadow/Constraint_Forecast.csv", "column": "Tref_max", "tz":"America/Los_Angeles", "agg": "mean", "window": "5m"},
#            "Tfre_min":  {"filename": "Shadow/Constraint_Forecast.csv", "column": "Tfre_min", "tz":"America/Los_Angeles", "agg": "mean", "window": "5m"},
#            "Tfre_max":  {"filename": "Shadow/Constraint_Forecast.csv", "column": "Tfre_max", "tz":"America/Los_Angeles", "agg": "mean", "window": "5m"},
            "SOC_min":  {"filename": "Shadow/Constraints_Forecast.csv", "column": "SOC_min", "tz":"America/Los_Angeles", "agg": "mean", "window": "1m"},
            "SOC_max":  {"filename": "Shadow/Constraints_Forecast.csv", "column": "SOC_max", "tz":"America/Los_Angeles", "agg": "mean", "window": "1m"},
            "uCool_min":  {"filename": "Shadow/Constraints_Forecast.csv", "column": "uCool_min", "tz":"America/Los_Angeles", "agg": "mean", "window": "1m"},
            "uCool_max":  {"filename": "Shadow/Constraints_Forecast.csv", "column": "uCool_max", "tz":"America/Los_Angeles", "agg": "mean", "window": "1m"},
            "uHeat_min":  {"filename": "Shadow/Constraints_Forecast.csv", "column": "uHeat_min", "tz":"America/Los_Angeles", "agg": "mean", "window": "1m"},
            "uHeat_max":  {"filename": "Shadow/Constraints_Forecast.csv", "column": "uHeat_max", "tz":"America/Los_Angeles", "agg": "mean", "window": "1m"},
            "uBattery_min":  {"filename": "Shadow/Constraints_Forecast.csv", "column": "uBattery_min", "tz":"America/Los_Angeles", "agg": "mean", "window": "1m"},
            "uBattery_max":  {"filename": "Shadow/Constraints_Forecast.csv", "column": "uBattery_max", "tz":"America/Los_Angeles", "agg": "mean", "window": "1m"},
            "uRef_min":  {"filename": "Shadow/Constraints_Forecast.csv", "column": "uRef_min", "tz":"America/Los_Angeles", "agg": "mean", "window": "1m"},
            "uRef_max":  {"filename": "Shadow/Constraints_Forecast.csv", "column": "uRef_max", "tz":"America/Los_Angeles", "agg": "mean", "window": "1m"},
            "uFreCool_min":  {"filename": "Shadow/Constraints_Forecast.csv", "column": "uFreCool_min", "tz":"America/Los_Angeles", "agg": "mean", "window": "1m"},
            "uFreCool_max":  {"filename": "Shadow/Constraints_Forecast.csv", "column": "uFreCool_max", "tz":"America/Los_Angeles", "agg": "mean", "window": "1m"},
            "Pmin":  {"filename": "Shadow/Constraints_Forecast.csv", "column": "Pmin", "tz":"America/Los_Angeles", "agg": "mean", "window": "1m"},
            "Pmax":  {"filename": "Shadow/Constraints_Forecast.csv", "column": "Pmax", "tz":"America/Los_Angeles", "agg": "mean", "window": "1m"}
        }
    },
    "price": {
        "type": "csv",
        "variables": {
            "pi_e":  {"filename": "Shadow/Price_Forecast.csv", "column": "pi_e", "tz":"America/Los_Angeles", "agg": "mean", "window": "1m"},
            "pi_d":  {"filename": "Shadow/Price_Forecast.csv", "column": "pi_d", "tz":"America/Los_Angeles", "agg": "mean", "window": "1m"},
            "P_est":  {"filename": "Shadow/Price_Forecast.csv", "column": "P_est", "tz":"America/Los_Angeles", "agg": "mean", "window": "1m"}
        }
    },
    "system": {
        "type": "influxdb",
        "variables": {
            "Tref": {"uuid": "5c69b4b6-22a0-561b-801b-72aee17c5a94", "window": "5m", "agg": "mean", "measurement": "timeseries"},
            "Trtu_west": {"uuid": "7d48d689-5cf8-50fd-98af-22dd9868b379", "window": "5m", "agg": "mean", "measurement": "timeseries"},
            "Trtu_east": {"uuid": "fd200d7e-0c46-53fc-87e4-6c8639b67b94", "window": "5m", "agg": "mean", "measurement": "timeseries"},
            "Tfre": {"uuid": "3f493b8d-0107-569f-8968-433f46de0fec", "window": "5m", "agg": "mean", "measurement": "timeseries"}
#            "SOC": {"uuid": "86f72439-35a3-4997-a14f-24f8a889b164", "window": "5m", "agg": "mean", "measurement": "timeseries"}
        }
    },

    "data_sink": {
        "setpoints": {
            "type": "csv",
            "filename": "Shadow/setpoints.csv"
        },
        "variables": {
            "Pbattery": {
                "type": "csv",
                "filename": "Shadow/setpoints.csv"
            },
            "Trtu_west": {
                "type": "csv",
                "filename": "Shadow/setpoints.csv"
            },
            "Trtu_east": {
                "type": "csv",
                "filename": "Shadow/setpoints.csv"
            },
            "Tref": {
                "type": "csv",
                "filename": "Shadow/setpoints.csv"
            },
            "Tfre": {
                "type": "csv",
                "filename": "Shadow/setpoints.csv"
            }
        }

    }
}
}

def get_config():

    return config

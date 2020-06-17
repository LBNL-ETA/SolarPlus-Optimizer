# -*- coding: utf-8 -*-

# change this file to baseline_config.py before executing

config={
    'max_battery_rate': 14000,
    'min_battery_rate': -14000,
    'max_battery_soc': 0.95,
    'min_battery_soc': 0.25,
    'historical_data_interval_minutes': 15,
    'battery_total_capacity': 27000,
    "data_manager_config": {
        "site": "blr",
        "source": {
            "influxdb": {
                "config_filename": "database_client/config.yaml",
                "section": "database"
            }
        },
        "baseline": {
            "type": "influxdb",
            "variables": {
                "building_load": {"uuid": "d2004400-349c-5015-8f20-e249953295a7", "window": "5m", "agg": "mean", "measurement": "timeseries"},
                "battery_soc": {"uuid": "0efc4fa5-755c-5c45-863a-c0c776ab7538", "window": "5m", "agg": "mean", "measurement": "timeseries"},
                "pv_generation": {"uuid": "fdfd7bbb-d2da-5b11-a8fa-58b231ab9802", "window": "5m", "agg": "mean", "measurement": "timeseries"}
            }
        },
        "data_sink": {
            "setpoints": {
                "type": "csv",
                # "type": "csv|xbos",
                "filename": "Shadow/setpoints_baseline.csv",
                "devices": {
                    # "emulated_battery/battery/actuation": {"real_power_setpoint": "battery_setpoint"}
                }
            },
            "variables": {
                "battery_setpoint": {
                    "type": "csv",
                    "filename": "Shadow/setpoints_baseline.csv"
                }
            }
        }
    }
}

def get_config():
    return config

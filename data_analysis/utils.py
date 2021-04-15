import datetime
import pandas as pd
from influxdb import DataFrameClient
import matplotlib
import matplotlib.pyplot as plt
import json
import pytz
import numpy as np
import yaml

with open('uuid_map.json') as fp:
    uuid_map = json.load(fp)
    
with open('config.yaml') as fp:
    config = yaml.safe_load(fp)
database_config = config.get('database')

client = DataFrameClient(
    host=database_config.get('host'), 
    port=database_config.get('port'), 
    username=database_config.get('username'), 
    password=database_config.get('password'), 
    database=database_config.get('database'), 
    ssl=database_config.get('ssl'), 
    verify_ssl=database_config.get('verify_ssl')
)

tz_local = pytz.timezone('America/Los_Angeles')
tz_utc = pytz.timezone('UTC')

uuid_dict = {
    'building_power': uuid_map['xbos/wattnode/building_main/PowerSum'],
    'freezer_power': uuid_map['xbos/wattnode/fre_comp_evapfan/PowerSum'],
    'ref_comp_power': uuid_map['xbos/wattnode/ref_comp/PowerSum'],
    'ref_fan_power': uuid_map['xbos/wattnode/ref_evapfan/PowerSum'],
    'hvac_west_power': uuid_map['xbos/wattnode/hvac_west_comp/PowerSum'],
    'hvac_east_power': uuid_map['xbos/wattnode/hvac_east_comp/PowerSum'],
    
    'building_energy': uuid_map['xbos/wattnode/building_main/EnergySum'],
    
    'east_temperature': uuid_map['xbos/flexstat/thermostat_east/space_temp'],
    'west_temperature': uuid_map['xbos/flexstat/thermostat_west/space_temp'],
    'freezer_temperature': uuid_map['xbos/parker/freezer/CabinetTemperature'],
    'ref_temperature': uuid_map['xbos/parker/refrigerator/CabinetTemperature'],
    
    'east_heating_sp': uuid_map['xbos/flexstat/thermostat_east/active_heating_setpt'],
    'east_cooling_sp': uuid_map['xbos/flexstat/thermostat_east/active_cooling_setpt'],
    'west_heating_sp': uuid_map['xbos/flexstat/thermostat_west/active_heating_setpt'],
    'west_cooling_sp': uuid_map['xbos/flexstat/thermostat_west/active_cooling_setpt'],
    'freezer_sp': uuid_map['xbos/parker/freezer/Setpoint'],
    'ref_sp': uuid_map['xbos/parker/refrigerator/Setpoint'],
    
    'soc_battery': '0efc4fa5-755c-5c45-863a-c0c776ab7538',
    'setpoint_battery': '276ea28f-0f74-5b3e-9ad1-f3b9f747dbe4',
    'pv_generation_battery': 'fdfd7bbb-d2da-5b11-a8fa-58b231ab9802',
    
    'oat_current': 'f7c1f2c8-c996-528c-ab3d-bdc96dc9cf72',
    'humidity_current': '7967b372-2699-57e1-bc15-7861bfe6d024',
    'windspeed_current': 'ac555599-0403-5bea-8441-f39a4e8e0dac',
    'cloudcover_current': '6cce3e9a-3822-551b-b13c-f4b874f3afa1',
    'solar_current': 'd15979be-7a63-5230-9e7b-d068d9f40b08',
    'sr_current': 'd15979be-7a63-5230-9e7b-d068d9f40b08',
    
    'oat_forecast': '69be4db0-48f5-592f-b5a1-e2e695f28ad1',
    'humidity_forecast': 'c2379487-3df3-5bfe-bd8d-5992d2381ed5',
    'windspeed_forecast': '837d0588-b30a-56ee-920f-cf366fa0871f',
    'cloudcover_forecast': '6f93857f-50a6-5b9f-8b94-0231f511b382',
    'solar_forecast': 'a8357adb-c59d-5316-a0e8-51d2b2948c75',
    
    'price_energy_dr': '3be4c234-a38a-5e73-9d53-4503751592be',
    'price_demand_dr': '90928e8d-df40-5e75-9ddb-7ee444bc187f',
    'pmax_dr': '522605a9-77b1-57e3-9fac-06dd83ab8e89',
    'pmin_dr': '6b42adf8-3a48-5ae7-bdc3-19226e602865',
    
    'bess_power_rtac': '02e68dd9-3802-537d-9156-e8a6066643fc',
    'island_type_rtac': '961bd5ae-2136-5d77-a2dc-b79cddddb42f',
    'pv_generation_rtac': 'd4102860-1f55-5e14-b02d-8bdb9e987676',
    'islanding_state_rtac': '97e29244-b2e3-5a7d-9971-ea9026cbc696'
}

def parse_dt_utc(dt):
    return tz_local.localize(datetime.datetime.strptime(dt, "%Y-%m-%d %H:%M:%S")).astimezone(tz_utc)

def current_uuid_data(client, uuid, st, et, column_name):
    st_utc = parse_dt_utc(st).strftime("%Y-%m-%dT%H:%M:%SZ")
    et_utc = parse_dt_utc(et).strftime("%Y-%m-%dT%H:%M:%SZ")
    query = "select value from timeseries where \"uuid\" = '%s' and time>= '%s' and time <= '%s'" % (uuid, st_utc, et_utc)
    df = client.query(query)['timeseries']
    df = df[['value']]
    df.columns = [column_name]
    return df

def forecast_uuid_data(client, uuid, st, et, column_name):
    st_utc = parse_dt_utc(st).strftime("%Y-%m-%dT%H:%M:%SZ")
    et_utc = parse_dt_utc(et).strftime("%Y-%m-%dT%H:%M:%SZ")
    query = "select value from timeseries where \"uuid\" = '%s' and \"prediction_step\" = '1' and time>= '%s' and time <= '%s'" % (uuid, st_utc, et_utc)
    df = client.query(query)['timeseries']
    df = df[['value']]
    df.columns = [column_name]
    return df

def get_data_section(client, endswith, st, et, uuid_dict, resample='1T', current=True):
    df_list = []
    for variable in uuid_dict:
        if variable.endswith(endswith):
            uuid = uuid_dict[variable]
            if current:
                df = current_uuid_data(client, uuid, st, et, column_name=variable[:variable.rfind('_')])
            else:
                df = forecast_uuid_data(client, uuid, st, et, column_name=variable[:variable.rfind('_')])
            df = df.resample(resample).mean()
            df_list.append(df)
    return pd.concat(df_list, axis=1)
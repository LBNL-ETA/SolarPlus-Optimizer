# author: Anand Prakash <akprakash@lbl.gov>

import pandas as pd
import json
import yaml
from influxdb import DataFrameClient
import datetime
import pytz

class Data_Client():
    def __init__(self):
        with open("config.yaml") as fp:
            self.config = yaml.safe_load(fp)

        self.db_config = self.config.get("database")
        self.uuid_map_filename = self.config.get('uuid_map_filename', 'uuid_map.json')
        with open(self.uuid_map_filename) as fp:
            self.uuid_map = json.load(fp)

        self.init_influx()

        self.tz_local = pytz.timezone("America/Los_Angeles")
        self.tz_utc = pytz.timezone("UTC")
        
        self.meters = ['ref_evapfan', 'ref_comp', 'fre_comp_evapfan', 'building_main', 'hvac_west_comp', 'hvac_east_comp']
        self.thermostats = ['thermostat_east', 'thermostat_west']
        self.parker_controllers = ['refrigerator', 'freezer']

    def init_influx(self):
        self.influx_client = DataFrameClient(
                   host = self.db_config.get('host'),
                   port = self.db_config.get('port'),
                   username = self.db_config.get('username'),
                   password = self.db_config.get('password'),
                   database = self.db_config.get('database'),
                   ssl = self.db_config.get('ssl'),
                   verify_ssl = self.db_config.get('verify_ssl'),
                )
        
    def get_uuid(self, device_name, variable):
        driver = None
        if device_name in self.parker_controllers:
            driver = "parker"
        elif device_name in self.meters:
            driver = "wattnode"
        elif device_name in self.thermostats:
            driver = "flexstat"
            
        key = 'xbos/{0}/{1}/{2}'.format(driver, device_name, variable)
        uuid = self.uuid_map[key]
        return uuid

    
    def get_data(self, uuid, start_time, end_time, measurement='timeseries'):
        st = pd.to_datetime(start_time).tz_localize(self.tz_local).tz_convert(self.tz_utc)
        et = pd.to_datetime(end_time).tz_localize(self.tz_local).tz_convert(self.tz_utc)

        st_str = st.strftime("%Y-%m-%dT%H:%M:%SZ")
        et_str = et.strftime("%Y-%m-%dT%H:%M:%SZ")

        q = "select value from %s where \"uuid\"=\'%s\'" % (measurement, uuid)
        q += " and time >= '%s' and time <= '%s'" % (st_str, et_str)

        df = self.influx_client.query(q)[measurement]

        return df

    
    def get_device_data(self, device_type, start_time, end_time, variables, resample_window='5T', agg_fn='mean'):
        if device_type == 'meters':
            device_list = self.meters
        elif device_type == 'parker_controllers':
            device_list = self.parker_controllers
        elif device_type == 'thermostats': 
            device_list = self.thermostats
            
        df_list = []
        for device in device_list:
            for variable in variables:
                uuid = self.get_uuid(device_name = device, variable=variable)
                df = self.get_data(uuid=uuid, start_time = start_time, end_time = end_time)
                df = df.resample(resample_window).agg(agg_fn)
                df.columns = ['{0}'.format(device+"_"+variable)]
                df_list.append(df)
        final_df = pd.concat(df_list, axis=1)
        return final_df

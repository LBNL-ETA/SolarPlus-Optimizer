import json
import itertools
import pandas as pd
import requests as req
import yaml
import random
import argparse
from struct import *
from influxdb import InfluxDBClient
from Influx_Dataframe_Client import Influx_Dataframe_Client

class API_Collection_Layer:

    def __init__(self,config_file,weather_section=None,db_section=None):
        '''
        Constructor
        Args:
        Returns:        None
        '''

        with open(config_file) as f:
            # use safe_load instead load
            skyConfig = yaml.safe_load(f)

        if(weather_section == None):
            weather_section = 'dark_sky'
        if(db_section == None):
            db_section = 'local_database_config'

        self.URL = skyConfig[weather_section]['url']
        self.API = skyConfig[weather_section]['api']
        self.COORDINATES = skyConfig[weather_section]['coordinates']

        self.test_client = Influx_Dataframe_Client(config_file,db_section)

    def push_current(self,database,measurement,current_timestamp,data):
        # Remove time from data field since this is field name is not allowed
        del(data['time'])
        send_json =   {
            'fields': data,
            'time': forecast_timestamp,
            'tags': {},
            'measurement': measurement
            }
        self.test_client.write_json(send_json,database)



    def push_forecast(self,database,measurement,forecast_timestamp,data):
        '''
        Push 48 hour forecast data from DarkSky
        Params:         database, measurement, forecast_timestamp, data
        Returns:        Dataframe containing wunderground data
        '''
        send_dict = []
        json_prediction = {}
        for x in range(len(data)):
            # Remove time field from fields as this field name is not allowed
            del(data[x]['time'])
            # Make all data types conistent
            data[x]['cloudCover'] = float(data[x]['cloudCover'])
            data[x]['precipIntensity'] = float(data[x]['precipIntensity'])
            data[x]['precipProbability'] = float(data[x]['precipProbability'])
            data[x]['windSpeed'] = float(data[x]['windSpeed'])
            data[x]['pressure'] = float(data[x]['pressure'])
            data[x]['visibility'] = float(data[x]['visibility'])
            data[x]['dewPoint'] = float(data[x]['dewPoint'])
            data[x]['windGust'] = float(data[x]['windGust'])
            #data[x][''] = float(data[x][''])

            json_prediction =   {
                'fields': data[x],
                'time': forecast_timestamp,
                'tags': {'hour_prediction': x},
                'measurement': measurement
                }
            send_dict.append(json_prediction)

        self.test_client.write_json(send_dict,database)


        return send_dict




    def get_data_dark_sky(self):
        '''
        Pull data from DarkSky
        Params:         None
        Returns:        Dataframe containing wunderground data
        '''
        send_dict = []
        json_prediction = {}
        database = 'dark_sky'
    #url = 'https://api.darksky.net/forecast/[key]/[latitude],[longitude]'
        url = self.URL + self.API + '/' + self.COORDINATES
        response = req.get(url)
        json_data = json.loads(response.text)
        print(url)
        if (response.status_code != 200):
            print("Error in retrieving data from Wunderground!")
            return None
        else:
            return json_data




######################## MAIN ########################



if __name__ == "__main__":
    # read arguments passed at .py file call
    # only argument is the yaml config file which specifies all the details
    # for connecting to the DarkSky API as well the local
    # influx databases
    parser = argparse.ArgumentParser()
    parser.add_argument("config", help="config file")

    args = parser.parse_args()
    config_file = args.config

    obj = API_Collection_Layer(config_file=config_file)
    api_data = obj.get_data_dark_sky()
    forecast_timestamp = api_data['currently']['time'] * 1000000000
    obj.push_forecast('dark_sky','forecast_48_hour',forecast_timestamp,api_data['hourly']['data'])
    obj.push_current('dark_sky','current_weather',forecast_timestamp,api_data['currently'])

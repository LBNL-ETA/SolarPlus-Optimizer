import os,sys
import json
import requests as req
import yaml
import argparse
import numpy as np
import pandas as pd
from pvlib import solarposition

# Add influx driver to path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
influx_folder='influx_dataframe_client'
sys.path.append(os.path.join(parent_dir, influx_folder))
from Influx_Dataframe_Client import Influx_Dataframe_Client
# DarkSky API documentation https://darksky.net/dev/docs#forecast-request



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
        for key in data:
            if isinstance(data[key],int):
                data[key] = float(data[key])

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
        Returns:        Dataframe containing darksky data
        '''
        send_dict = []
        json_prediction = {}
        for x in range(len(data)):
            # Remove time field from fields as this field name is not allowed
            del(data[x]['time'])
            # Make all data types conistent
            for key in data[x]:
                if isinstance(data[x][key],int):
                    data[x][key] = float(data[x][key])


            json_prediction =   {
                'fields': data[x],
                'time': forecast_timestamp,
                'tags': {'hour_prediction': x},
                'measurement': measurement
                }
            send_dict.append(json_prediction)

        self.test_client.write_json(send_dict,database)


        return send_dict

    # datetime should include timezone information, otherwise UTC time by default
    alt_ang = solarposition.get_solarposition(datetime,lat,lon)['elevation']
    sin_alt = np.sin(np.radians(alt_ang))
    zh_solar_const = 1355 # W/m2, solar constant used by Zhang-Huang model
    solar_const = 1367 # general solar constant

    def solar_model_ZhHu(sin_alt,cloud_cover,temperature,rel_hum,wind_speed):
        '''
        Estimate Global Horizontal Irradiance (GHI) from Zhang-Huang solar forecast model
        Params: sin_alt, sine of solar altitude
                cloud_cover: [0,1];
                temperature: degC;
                relative humidity: %;
                wind_speed: m/s;
        Returns: estimated GHI
        '''
        c0 = 0.5598; c1 = 0.4982; c2 = -0.6762; c3 = 0.02842
        c4 = -0.00317; c5 = 0.014; d = -17.853; k = 0.843
        estimated_ghi = pd.Series(index=datetime)
        deltaT = pd.Series(index=datetime)
        for n in range(len(estimated_ghi)):
            deltaT[n] = temperature[n]-temperature[n-3]
            estimated_ghi[n] = (zh_solar_const*np.sin(np.radians(alt_ang[n]))*(c0+c1*cloud_cover[n]
                        +c2*cloud_cover[n]**2+c3*deltaT[n]+c4*rel_hum[n]*100+c5*wind_speed[n])+d)/k
            estimated_ghi[n] = estimated_ghi[n] if estimated_ghi[n]>0 else 0

        return estimated_ghi

    def Perez_split(ghi,sin_alt):
        '''
        Estimate beam radiation and diffuse radiation from GHI and solar altitude
        Params: GHI, W/m2
                sin_alt, sine of solar altitude
        Returns: beam_rad, beam radiation, W/m2
                 diff_rad, diffuse radiation, W/m2
        '''
        clear_index_kt = ghi/(solar_const*sin_alt)
        clear_index_ktc = 0.4268 + 0.1934 * sin_alt
        clear_index_kds = pd.Series(index=ghi.index)
        for i in range(len(ghi)):
            if clear_index_kt[i] < clear_index_ktc[i]:
                clear_index_kds[i] = (3.996-3.862*sin_alt[i]+1.54*(sin_alt[i])**2) * (clear_index_kt[i])**3
            else:
                clear_index_kds[i] = clear_index_kt[i]-(1.107+0.03569*sin_alt[i]+1.681*(sin_alt[i])**2)
                                    *(1.0-clear_index_kt[i])**3
        # Calculate direct normal radiation, W/m2
        beam_rad = zh_solar_const*sin_alt*clear_index_kds*(1.0-clear_index_kt)/(1.0-clear_index_kds)
        # Calculation diffuse horizontal radiation, W/m2
        diff_rad = zh_solar_const*sin_alt*(clear_index_kt-clear_index_kds)/(1.0-clear_index_kds)

        return beam_rad, diff_rad

    def get_data_dark_sky(self):
        '''
        Pull data from DarkSky
        Params:         None
        Returns:        Dataframe containing darksky data
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
            print("Error in retrieving data from DarkSky!")
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
    obj.push_forecast('dark_sky','forecast_48_hour_2',forecast_timestamp,api_data['hourly']['data'])
    obj.push_current('dark_sky','current_weather_3',forecast_timestamp,api_data['currently'])
    print(api_data['hourly']['data'][0])

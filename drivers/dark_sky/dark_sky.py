import os,sys
import json
import requests as req
import yaml
import argparse
import numpy as np
import pandas as pd
from pvlib import solarposition, irradiance

class API_Collection_Layer:
    '''
    Weather API to query and calculate the following parameters to be used in MPC;
    queried parameters:
        cloudCover: total cloud cover, unit: [0,1];
        temperature: outdoor dry bulb, unit: degC;
        humidity: relative humidity, unit: %;
        windSpeed: wind speed, unit: m/s;
    calculated parameters:
        sin_alt, sine of solar altitude, unit: [-1, 1];
        deltaT: temperature difference, unit: degC;
        estimated_ghi: estimated global horizontal irradiance, unit: W/m2;
        beam_rad, beam radiation, W/m2;
        diff_rad, diffuse radiation, W/m2;
        poa_pv: plane of array solar radiation on photovoltaic panels, unit: W/m2
        poa_win: plane of array solar radiation on windows, unit: W/m2

    '''

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
        self.lat = skyConfig[weather_section]['lat']
        self.lng = skyConfig[weather_section]['lng']
        self.COORDINATES = "%f,%f"%(self.lat, self.lng)

    def solar_model_ZhHu(self, forecast_df, sin_alt, zh_solar_const):
        '''
        Estimate Global Horizontal Irradiance (GHI) from Zhang-Huang solar forecast model
        Params: sin_alt, sine of solar altitude, unit: [-1, 1]
                forecast_df should include the following columns:
                cloudCover: total cloud cover, unit: [0,1];
                temperature: outdoor dry bulb, unit: degC;
                humidity: relative humidity, unit: %;
                windSpeed: wind speed, unit: m/s;
        Returns: deltaT: temperature difference, unit: degC
                 estimated_ghi: estimated global horizontal irradiance, unit: W/m2;
        '''

        # df = forecast_df.copy()

        c0 = 0.5598
        c1 = 0.4982
        c2 = -0.6762
        c3 = 0.02842
        c4 = -0.00317
        c5 = 0.014
        d = -17.853
        k = 0.843

        shift_temp = pd.Series(data=np.roll(forecast_df.temperature, 3), index=forecast_df.index)
        forecast_df['deltaT'] = forecast_df['temperature'] - shift_temp
        forecast_df['estimated_ghi'] = (zh_solar_const * sin_alt * (c0 + c1 * forecast_df['cloudCover']
                                        + c2 * forecast_df['cloudCover']**2 + c3 * forecast_df['deltaT'] + c4 * forecast_df['humidity'] * 100
                                        + c5 * forecast_df['windSpeed'])+d)/k
        forecast_df.loc[forecast_df.loc[forecast_df.estimated_ghi <= 0].index, 'estimated_ghi'] = 0

        return forecast_df

    def Perez_split(self, forecast_df):
        '''
        Estimate beam radiation and diffuse radiation from GHI and solar altitude
        Params: forecast_df includes the estimated GHI
        Returns: beam_rad, beam radiation, W/m2
                 diff_rad, diffuse radiation, W/m2
        '''

        # datetime should include timezone information, otherwise UTC time by default
        alt_ang = solarposition.get_solarposition(forecast_df.index, self.lat, self.lng)['elevation']
        sin_alt = np.sin(np.radians(alt_ang))
        zh_solar_const = 1355 # W/m2, solar constant used by Zhang-Huang model
        solar_const = 1367 # general solar constant

        df = self.solar_model_ZhHu(forecast_df=forecast_df, sin_alt=sin_alt,  zh_solar_const=zh_solar_const)

        clear_index_kt = df['estimated_ghi']/(solar_const*sin_alt)
        clear_index_ktc = 0.4268 + 0.1934 * sin_alt

        diff = (clear_index_kt < clear_index_ktc)*1  # *1 converts boolean to integer
        clear_index_kds = diff * ((3.996 - 3.862 * sin_alt + 1.54 * (sin_alt)**2) * (clear_index_kt)**3) + \
                        (1-diff) * (clear_index_kt - (1.107 + 0.03569 * sin_alt + 1.681 * (sin_alt)**2) * (1.0-clear_index_kt)**3)

        # Calculate direct normal radiation, W/m2
        df['beam_rad'] = zh_solar_const * sin_alt * clear_index_kds * (1.0 - clear_index_kt) / (1.0 - clear_index_kds)
        # Calculate diffuse horizontal radiation, W/m2
        df['diff_rad'] = zh_solar_const * sin_alt * (clear_index_kt - clear_index_kds) / (1.0 - clear_index_kds)
        return df

    def plane_of_array(self, df):
        """
        :param df: data frame includes GHI, beam_rad, diff_rad
        :return: df with plane of array solar radiation on pv and windows
                poa_pv: plane of array solar radiation on photovoltaic panels, unit: W/m2
                poa_win: plane of array solar radiation on windows, unit: W/m2
        """
        pv_tilt = 8
        pv_azimuth = 37
        albedo = 0.2
        win_tilt = 90
        win_azimuth = 0
        datetime = df.index
        alt_ang = solarposition.get_solarposition(datetime, self.lat, self.lng)['elevation']
        azi_ang = solarposition.get_solarposition(datetime, self.lat, self.lng)['azimuth']
        df['poa_pv'] = irradiance.get_total_irradiance(pv_tilt, pv_azimuth, alt_ang, azi_ang, df['beam_rad'],
                                                       df['estimated_ghi'], df['diff_rad'], albedo)['poa_global']
        df['poa_win'] = irradiance.get_total_irradiance(win_tilt, win_azimuth, alt_ang, azi_ang, df['beam_rad'],
                                                       df['estimated_ghi'], df['diff_rad'], albedo)['poa_global']
        return df

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

        if (response.status_code != 200):
            print("Error in retrieving data from DarkSky!")
            return None
        else:
            hourly_df = pd.DataFrame.from_dict(json_data['hourly']['data'])
            hourly_df.time = pd.to_datetime(hourly_df.time, unit='s', utc=True)
            hourly_df = hourly_df.set_index('time')

            hourly_df = self.Perez_split(forecast_df=hourly_df)
            hourly_df = self.plane_of_array(df=hourly_df)
            hourly_df = hourly_df.reset_index()
            hourly_df['time'] = hourly_df['time'].astype(int)
            hourly_dict = hourly_df.drop(columns=['precipType']).to_dict('records')
            json_data['hourly']['data'] = hourly_dict
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
    print(json.dumps(api_data))

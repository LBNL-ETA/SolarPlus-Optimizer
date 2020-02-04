# -*- coding: utf-8 -*-
"""
This script prepares weather input data for parameter estimation.
"""

import numpy as np
import pandas as pd
from pvlib import solarposition, irradiance

def solar_model_ZhHu(forecast_df, sin_alt, zh_solar_const):
    '''
    Estimate Global Horizontal Irradiance (GHI) from Zhang-Huang solar forecast model
    Params: sin_alt, sine of solar altitude, unit: [-1, 1]
            forecast_df should include the following columns:
            cloudCover: total cloud cover, unit: [0,1];
            temperature: outdoor dry bulb, unit: degF;
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
    # forecast_df['temperature_c'] = (forecast_df['temperature'] - 32) * 5.0/9.0
    forecast_df['temperature_c'] = forecast_df['temperature']
    shift_temp = pd.Series(data=np.roll(forecast_df.temperature_c, 3), index=forecast_df.index)
    forecast_df['deltaT'] = forecast_df['temperature_c'] - shift_temp
    forecast_df['estimated_ghi'] = (zh_solar_const * sin_alt * (c0 + c1 * forecast_df['cloudCover']
                                    + c2 * forecast_df['cloudCover']**2 + c3 * forecast_df['deltaT'] + c4 * forecast_df['humidity'] * 100
                                    + c5 * forecast_df['windSpeed'])+d)/k
    forecast_df.loc[forecast_df.loc[forecast_df.estimated_ghi <= 0].index, 'estimated_ghi'] = 0

    return forecast_df

def Perez_split(forecast_df):
    '''
    Estimate beam radiation and diffuse radiation from GHI and solar altitude
    Params: forecast_df includes the estimated GHI
    Returns: beam_rad, beam radiation, W/m2
             diff_rad, diffuse radiation, W/m2
    '''

    # datetime should include timezone information, otherwise UTC time by default
    lat = 37.8771
    lng = -122.2485
    alt_ang = solarposition.get_solarposition(forecast_df.index, lat, lng)['elevation']
    sin_alt = np.sin(np.radians(alt_ang))
    zh_solar_const = 1355 # W/m2, solar constant used by Zhang-Huang model
    solar_const = 1367 # general solar constant

    df = solar_model_ZhHu(forecast_df=forecast_df, sin_alt=sin_alt,  zh_solar_const=zh_solar_const)

    clear_index_kt = df['estimated_ghi']/(solar_const*sin_alt)
    clear_index_ktc = 0.4268 + 0.1934 * sin_alt

    diff = (clear_index_kt < clear_index_ktc)*1  # *1 converts boolean to integer
    clear_index_kds = diff * ((3.996 - 3.862 * sin_alt + 1.54 * (sin_alt)**2) * (clear_index_kt)**3) +                     (1-diff) * (clear_index_kt - (1.107 + 0.03569 * sin_alt + 1.681 * (sin_alt)**2) * (1.0-clear_index_kt)**3)

    # Calculate direct normal radiation, W/m2
    df['beam_rad'] = zh_solar_const * sin_alt * clear_index_kds * (1.0 - clear_index_kt) / (1.0 - clear_index_kds)
    # Calculate diffuse horizontal radiation, W/m2
    df['diff_rad'] = zh_solar_const * sin_alt * (clear_index_kt - clear_index_kds) / (1.0 - clear_index_kds)
    return df

def plane_of_array(df):
    """
    :param df: data frame includes GHI, beam_rad, diff_rad
    :return: df with plane of array solar radiation on pv and windows
            poa_pv: plane of array solar radiation on photovoltaic panels, unit: W/m2
            poa_win: plane of array solar radiation on windows, unit: W/m2
    """
    lat = 37.8771
    lng = -122.2485
    pv_tilt = 8
    pv_azimuth = 37
    albedo = 0.2
    win_tilt = 90
    win_azimuth = 0
    datetime = df.index
    alt_ang = solarposition.get_solarposition(datetime, lat, lng)['elevation']
    azi_ang = solarposition.get_solarposition(datetime, lat, lng)['azimuth']
    df['poa_pv'] = irradiance.get_total_irradiance(pv_tilt, pv_azimuth, alt_ang, azi_ang, df['beam_rad'],
                                                   df['estimated_ghi'], df['diff_rad'], albedo)['poa_global']
    df['poa_win'] = irradiance.get_total_irradiance(win_tilt, win_azimuth, alt_ang, azi_ang, df['beam_rad'],
                                                   df['estimated_ghi'], df['diff_rad'], albedo)['poa_global']
    return df

hourly_df = pd.read_csv('darksky_201911.csv',index_col='time')
hourly_df = Perez_split(forecast_df=hourly_df)
hourly_df = plane_of_array(df=hourly_df)

start_time = '2019-11-06 00:00:00'
weather_input = hourly_df[['temperature_c','poa_pv','poa_win']].loc[start_time:]
weather_input['temperature_k'] = weather_input['temperature_c']+273.15
weather_input.to_csv('weather_input_201911.csv')

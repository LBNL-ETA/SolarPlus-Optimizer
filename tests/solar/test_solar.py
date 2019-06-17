# -*- coding: utf-8 -*-
"""
Created on Wednesday Feb 27 13:55:47 2019
@author: Kun Zhang

This module contains unit tests of solar forecast model.

"""

from __future__ import division
import unittest
import pandas as pd
from drivers.dark_sky.dark_sky import API_Collection_Layer as api
import matplotlib.pyplot as plt
import os
import pyfunnel as pf
import numpy as np
import shutil

class functional(unittest.TestCase):
    def setUp(self):
        self.start_day = '2017-08-05'
        self.end_day = '2017-08-11'
        config = os.path.abspath(os.path.join(__file__,'..','..','..','drivers','dark_sky',"config.yaml"))
        self.api = api(config_file=config)
        estimated_df = os.path.abspath(os.path.join(__file__,'..','fixtures','estimated_df.csv'))
        self.estimated_df = pd.read_csv(estimated_df,index_col='time')

    def ds(self,start_day,end_day):
        darksky = os.path.join(os.path.dirname(__file__),'fixtures','darksky_201707-201805.csv')
        darksky = pd.read_csv(darksky,index_col='time',parse_dates=True)
        ds = darksky.loc[start_day:end_day]
        return ds

    def syn(self,start_day,end_day):
        # read in solar radiation data from Synoptic data for LBNL1
        # assume air_temp_set_1 to be 2m temperature while air_temp_set_2 to be 10m temperature
        LBNL = os.path.join(os.path.dirname(__file__),'fixtures','LBNL1_solar_radiation.csv')
        synoptic = pd.read_csv(LBNL,skiprows=12,na_values = ['no info', '.'],
                               names=['Station','UTC','T_2m','temperature','humidity','windSpeed','GHI'],
                               index_col='UTC',parse_dates=True)
        synoptic.index = pd.to_datetime(synoptic.index,utc=True)
        # resample 15min data to hourly in order to compare with hourly darksky data
        synoptic = synoptic.resample('H').mean()
        syn = synoptic.loc[start_day:end_day]
        return syn

    def test_forecast(self):
        ds_sum = self.ds(self.start_day,self.end_day)
        syn_sum = self.syn(self.start_day,self.end_day)
        datetime = ds_sum.index
        estimated_df = self.api.Perez_split(ds_sum)
        measured_ghi = syn_sum['GHI']
        # self.api.plane_of_array(ds_sum).to_csv('df_all_solar.csv')

        results_dir = os.path.abspath(os.path.join(__file__,'..','results'))
        pf.compareAndReport(
                    xReference = pd.to_datetime(self.estimated_df.index).astype(np.int64)/1E9,
                    xTest = pd.to_datetime(estimated_df.index).astype(np.int64)/1E9,
                    yReference = self.estimated_df['estimated_ghi'],
                    yTest = estimated_df['estimated_ghi'],
                    atolx = 1,
                    rtoly = 0.01,
                    outputDirectory = results_dir
                    )
        error_df = pd.read_csv(os.path.join(results_dir, 'errors.csv'))
        # pf.plot_funnel(results_dir)
        self.assertAlmostEqual(error_df.iloc(axis=1)[1].max(),0)
        shutil.rmtree(results_dir)

        fig, ax1 = plt.subplots(figsize=[18,8])
        line1 = ax1.plot(datetime,measured_ghi,label='measured')
        line2 = ax1.plot(datetime,estimated_df['estimated_ghi'],label='estimated (darksky inputs)')
        ax1.set_xlabel('Time')
        ax1.set_ylabel('Global Horizontal Radiation ($W/m^{2}$)')
        ax1.grid()
        ax2 = ax1.twinx()
        line3 = ax2.plot(datetime,estimated_df['cloudCover'],'y-.')
        ax2.set_ylabel('Cloud cover (-)')
        lines = line1+line2+line3
        labs = [l.get_label() for l in lines]
        ax1.legend(lines, labs, loc='upper left')
        plt.savefig("Estimated GHI.png")

        fig, ax1 = plt.subplots(figsize=[18,8])
        ax1.plot(datetime,estimated_df['estimated_ghi'],label="global horizontal radiation")
        ax1.plot(datetime,estimated_df['beam_rad'],label="beam radiation")
        ax1.plot(datetime,estimated_df['diff_rad'],label='diffuse radiation')
        ax1.set_xlabel('Time')
        ax1.set_ylabel('Solar radiation ($W/m^{2}$)')
        ax1.legend()
        ax1.grid()
        plt.savefig("Beam and diffuse radiation.png")


if __name__ == '__main__':
    unittest.main()

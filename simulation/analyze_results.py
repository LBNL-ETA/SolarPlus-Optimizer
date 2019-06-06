# -*- coding: utf-8 -*-
"""
Created on Fri May 10 09:52:47 2019

@author: dhbubu
"""

import pandas as pd
import os
from matplotlib import pyplot as plt
import numpy as np

def emulation():
    '''Emulation measurements.
    
    '''
    
    df_all = _concat_csvs_to_df('emu_measurements')
    plot_vars = dict()

    plot_vars[0] = {'Vars':dict(), 'Unit':'K'}
    plot_vars[0]['Vars'] = {'Trtu':{'Title':'Average Store Temperature','Color':'r'},
                            'Tref':{'Title':'Refrigerator Temperature','Color':'b'},
                            'Tfre':{'Title':'Freezer Temperature','Color':'g'}}

    plot_vars[1] = {'Vars':dict(), 'Unit':'W'}
    plot_vars[1]['Vars'] = {'Pbattery':{'Title':'Battery Power','Color':'k'},
                              'Prtu':{'Title':'RTU Cooling Power','Color':'r'},
                              'Pref':{'Title':'Refrigerator Cooling Power','Color':'b'},
                              'Pfre':{'Title':'Freezer Cooling Power','Color':'g'}}

    plot_vars[2] = {'Vars':dict(), 'Unit':'-'}
    plot_vars[2]['Vars'] = {'SOC':{'Title':'Battery SOC','Color':'k'}}
    
    plot_vars[3] = {'Vars':dict(), 'Unit':'kW'}
    plot_vars[3]['Vars'] = {'Pnet':{'Title':'Net Store Power', 'Color':'k'}}
                 

    _plot_all(df_all, plot_vars)
    
def mpc():
    '''MPC measurement signals.
    
    '''

    df_list = _join_csvs_to_df_list('measurements')  
    plot_vars = {'SOC':'Battery SOC [-]',
                 'Trtu':'Average Store Temperature [K]',
                 'Tref': 'Refrigerator Temperature [K]',
                 'Tfre': 'Freezer Temperature [K]'}
                 
    _plot_each(df_list, plot_vars)

def _concat_csvs_to_df(name):
    '''Concatenate all csvs into one dataframe.
    
    Parameters
    ----------
    name : str
        Name of csv files, except the iteration number.
    
    Returns
    -------
    df_all : pandas DataFrame
        Contains all data concatenated from all csvs.
        
    '''
    
    df_all = pd.DataFrame()
    for i in range(24):
    #for i in range(48)[24:48]:
        control_csv = os.path.abspath(os.path.join(__file__,'..','output', '{0}_{1}.csv'.format(name,i)))
        df = pd.read_csv(control_csv, index_col='Time')
        df.index = pd.to_datetime(df.index)
        df_all = pd.concat([df_all,df])
        
    return df_all
    
def _join_csvs_to_df_list(name):
    '''Group all csvs into one dataframe list.
    
    Parameters
    ----------
    name : str
        Name of csv files, except the iteration number.
    
    Returns
    -------
    df_list : list of pandas DataFrame
        Contains all data from all csvs.
        
    '''
    
    df_list = []
    for i in range(24):
        control_csv = os.path.abspath(os.path.join(__file__,'..','output', '{0}_{1}.csv'.format(name,i)))
        df = pd.read_csv(control_csv, index_col='Time')
        df.index = pd.to_datetime(df.index)
        df_list.append(df)
        
    return df_list
    
def _plot_all(df,plot_vars):
    '''Plot the dataframe
    
    '''
    
    n = len(plot_vars.keys())
    f,ax = plt.subplots(n,1, sharex=True)
    for i in plot_vars.keys():
        for v in plot_vars[i]['Vars']:
            if plot_vars[i]['Unit'] == 'K':
                df[v] = (df[v]-273.15)*9/5+32
            if plot_vars[i]['Unit'] == 'W':
                df[v] = df[v]/1000
            ax[i].plot(df[v],label=plot_vars[i]['Vars'][v]['Title'],color=plot_vars[i]['Vars'][v]['Color'], alpha=0.75)
        ax[i].legend()
    plt.show()
    
def _plot_each(df_list,plot_vars):
    '''Plot each of the dataframes int he list
    
    '''
    
    for var in plot_vars.keys():
        plt.figure()
        plt.title(var)
        for df in df_list:
            df[var].plot()
    plt.show()
    
if __name__ == '__main__':
    mpc()
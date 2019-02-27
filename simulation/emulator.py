# -*- coding: utf-8 -*-
"""
Created on Mon Oct 29 14:40:51 2018

@author: dhb-lx
"""

import os
from mpcpy import systems, exodata, units, variables


class emulator(object):

    def __init__(self, outdir):
        self.outdir = outdir
        # Weather
        csvpath_weather = os.path.join('data','Temperature.csv')
        weather_vm = {'Outdoor':('weaTDryBul', units.degC)}
        geography = (40.88,-124.0)
        self.weather = exodata.WeatherFromCSV(csvpath_weather, weather_vm, geography)
        # Setpoints
        csvpath_setpoints = os.path.join('data','setpoints.csv')
        setpoints_vm = {'Trtu_heat': ('setHeat', units.K),
                        'Trtu_cool': ('setCool', units.K),
                        'Tref': ('setRef', units.K),
                        'Tfre': ('setFre', units.K),
                        'uCharge':('uCharge', units.unit1),
                        'uDischarge':('uDischarge', units.unit1)};
        self.setpoints = exodata.OtherInputFromCSV(csvpath_setpoints, setpoints_vm)
        # Emulator
        # Model information
        mopath = 'models/SolarPlus.mo'
        modelpath = 'SolarPlus.Building.Emulation.Store'
        libraries = []
        self.moinfo = (mopath, modelpath, libraries)
        # Model measurements
        meas_list = ['Trtu', 'Tref', 'Tfre', 'Pnet', 'Prtu', 'Pref', 'Pfre','Pcharge', 'Pdischarge', 'SOC']
        sample_rate = 300
        self.measurements = dict()
        for meas in meas_list:
            self.measurements[meas] = {'Sample' : variables.Static('{0}_sample'.format(meas), sample_rate, units.s)};

    def simulate(self, start_time, final_time):
        # Update exodata
        self.weather.collect_data(start_time, final_time)
        self.setpoints.collect_data(start_time, final_time)
        # Instantiate emulator if initial
        if start_time is not 'continue':
            self.building = systems.EmulationFromFMU(self.measurements,
                                                     moinfo=self.moinfo,
                                                     weather_data = self.weather.data,
                                                     other_inputs = self.setpoints.data)

        # Simulate fmu
        self.building.collect_measurements(start_time, final_time)
        # Save outputs
        emu_measurements = self.building.display_measurements('Measured')

        return emu_measurements

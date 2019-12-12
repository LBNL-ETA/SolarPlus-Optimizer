__author__ = 'Olivier Van Cutsem, Pranav Gupta'

import json
import os
from datetime import timedelta

import electricitycostcalculator
import pandas as pd
from dateutil.parser import parse
from electricitycostcalculator.cost_calculator.cost_calculator import CostCalculator
from electricitycostcalculator.cost_calculator.tariff_structure import *
from electricitycostcalculator.openei_tariff.openei_tariff_analyzer import *

costcalculator_path = os.path.dirname(electricitycostcalculator.__file__) + '/'


def read_from_json(filename):
    """ Read file and store in JSON object.

    Parameters
    ----------
    filename    : str
        Full path of the file to be read.

    Returns
    -------
    Dict
        JSON object of the file.

    """
    with open(filename, 'r') as input_file:
        data_json = json.load(input_file)
        return data_json


class DREventManager:

    def __init__(self, freq):

        # Dictionary of default events
        self.default_events = {}

        # List of custom DR events
        self.custom_dr_events = []

        # CostCalculator instance.
        self.__tariff_manager = CostCalculator()

        self.FORECAST_FREQUENCY = freq

    @staticmethod
    def get_df_powerconstraints(l_timeframe, l_power_constraint):
        """ Create and fill a pandas dataframe with power information between multiple timeframe.

        Parameters
        ----------
        l_timeframe         : list(tuple)
            [(startdate, enddate)...]
        l_power_constraint  : dict
            Power data.

        Returns
        -------
        pd.DataFrame()
            Dataframe with power data.

        """
        df = None
        for timeframe, power_constraint in zip(l_timeframe, l_power_constraint):
            st, et = timeframe
            index = pd.date_range(st, et, freq=DEFAULT_DT)
            new_df = pd.DataFrame(data=len(index) * [power_constraint], index=index, columns=['power'])
            if df is None:
                df = new_df
            else:
                df.append(new_df)
        return df

    def add_default_dr_events(self, type_dr, dr_raw_data):
        """  Add all the default DR events to DREventManager.

        Parameters
        ----------
        type_dr     : str
            Type of DR mode.
        dr_raw_data : dict
            DR event data.
        """
        self.default_events[type_dr] = dr_raw_data

    def add_dr_event(self, type_dr, dr_raw_data):
        """ Add custom DR event to DREventManager.

        Parameters
        ----------
        type_dr     : str
            Type of DR mode.
        dr_raw_data : dict
            DR event data.
        """
        ret_dict = self.decode_rawjson(type_dr, dr_raw_data)
        self.custom_dr_events.append(ret_dict)

    def get_available_default_events(self, type_dr, time_frame):
        """ Get all default events in the given time frame.

        Parameters
        ----------
        type_dr     : str
            Type of DR mode.
        time_frame  : tuple
            (start_date, end_date)
        filename    : str
            Full path of the file containing default event data.

        Returns
        -------
        dict
            Dictionary of default event
        """
        st, et = time_frame
        result = {}

        if type_dr == 'dr-prices':
            result['startdate'] = st
            result['enddate'] = et
            result['data_dr'] = self.get_df_tariff(self.default_events[type_dr]['type'], (st, et),
                                                   self.default_events[type_dr]['data'])
        else:
            raise ValueError('type_dr is not one of valid DR Modes.')

        return result

    def get_available_events(self, type_dr, time_frame):
        """ Get all events in the given time frame.

        Parameters
        ----------
        type_dr     : str
            Type of DR mode.
        time_frame  : tuple
            (start_date, end_date)

        Returns
        -------
        list(dict)
            List of available events.

        """
        avail_events = self.custom_dr_events

        # Filter by type of DR
        avail_events = [ev for ev in avail_events if ev['type_dr'] == type_dr]

        # Filter by time frame
        st, et = time_frame
        avail_events = [x for x in avail_events if (st <= x['startdate'] <= et) or (st <= x['enddate'] <= et) or (
                x['startdate'] <= st and x['enddate'] >= et)]

        if type_dr == 'dr-prices':
            avail_events = [ev['data_dr'][(ev['data_dr'].index >= st) & (ev['data_dr'].index <= et)].to_json() for ev in
                            avail_events]
        # If type_dr == 'dr-limit' then no need to filter based on index because ev['data_dr'] is not a dataframe

        return avail_events

    def decode_rawjson(self, type_dr, raw_data):
        """ Decode the custom DR events json file.

        Parameters
        ----------
        type_dr     : str
            Type of DR mode.
        raw_data    : dict
            DR event data.

        Returns
        -------
        dict
            Result that corresponds to the different DR modes.
        """
        ret_dict = {}

        if type_dr == 'dr-prices':
            ret_dict['type_dr'] = 'dr-prices'
            ret_dict['startdate'] = raw_data["start-date"]
            ret_dict['enddate'] = raw_data["end-date"]
            ret_dict['data_dr'] = self.get_df_tariff(raw_data["type"], (raw_data["start-date"], raw_data["end-date"]),
                                                     raw_data["data"])

        elif type_dr == 'dr-limit' or type_dr == 'dr-shed' or type_dr == 'dr-track':
            raw_data = raw_data["data"]
            ret_dict['type_dr'] = type_dr
            ret_dict['startdate'] = raw_data["start-date"]
            ret_dict['enddate'] = raw_data["end-date"]
            if type_dr == 'dr-track':
                ret_dict['data_dr'] = raw_data['profile']
            else:
                ret_dict['data_dr'] = raw_data['power']

        elif type_dr == 'dr-shift':
            raw_data = raw_data["data"]

            start_date = {
                'start-date-take': raw_data["start-date-take"],
                'start-date-relax': raw_data["start-date-relax"]
            }
            end_date = {
                'end-date-take': raw_data["end-date-take"],
                'end-date-relax': raw_data["end-date-relax"]
            }
            power = {
                'power-take': raw_data['power-take'],
                'power-relax': raw_data['power-relax']
            }
            ret_dict['startdate'] = start_date
            ret_dict['enddate'] = end_date
            ret_dict['data_dr'] = power

        else:
            raise ValueError('type_dr is none of valid DR Modes.')

        return ret_dict

    def get_df_tariff(self, type_tariff, date_period, raw_json_data):
        """ Return a Pandas dataframe of electricity prices.

        Parameters
        ----------
        type_tariff     : str
            'price-rtp' or 'price-tou'
        date_period     : tuple
            (start_date, end_date)
        raw_json_data   : dict
            Dict containing name of json file to read from.

        Returns
        -------
        pd.DataFrame
            Dataframe containing electricity prices.
        """
        start_date, end_date = date_period

        if type_tariff == 'price-tou':

            if 'tariff-json' in raw_json_data:
                # Init the CostCalculator with the tariff data
                tariff_data = OpenEI_tariff()
                tariff_data.read_from_json(costcalculator_path + raw_json_data['tariff-json'])

                # Now __tariff_manager has the blocks that defines the tariff
                tariff_struct_from_openei_data(tariff_data, self.__tariff_manager)

                # Get the price signal
                if self.FORECAST_FREQUENCY == '15min':
                    timestep = TariffElemPeriod.QUARTERLY
                else:
                    print('price has hourly timestep...')
                    timestep = TariffElemPeriod.HOURLY

                start_date_sig = parse(start_date)
                end_date_sig = parse(end_date)
                price_df, map = self.__tariff_manager.get_electricity_price((start_date_sig, end_date_sig), timestep)

            elif 'energy_prices' in raw_json_data and 'demand_prices' in raw_json_data:
                assert len(raw_json_data['energy_prices']) == len(raw_json_data['demand_prices'])
                st, et = parse(start_date), parse(end_date)
                delta_sec = (et - st).total_seconds()

                if self.FORECAST_FREQUENCY == '15min':
                    step = timedelta(minutes=15)  # CHECK: add self.FORECAST_FREQUENCY HERE
                else:
                    raise NotImplementedError('Only 15min frequency works for now.')
                assert len(raw_json_data['energy_prices']) == (delta_sec / step.total_seconds())

                array = []
                for index, i in enumerate(range(0, int(delta_sec), int(step.total_seconds()))):
                    array.append([st + timedelta(seconds=i),
                                  raw_json_data['energy_prices'][index],
                                  raw_json_data['demand_prices'][index]])
                price_df = pd.DataFrame(array, columns=['timestamp',
                                                        'customer_energy_charge',
                                                        'customer_demand_charge_tou'])
                price_df.set_index(price_df.columns[0], inplace=True)
            else:
                raise KeyError('cannot find tariff-json or (energy_prices and demand_prices)')

            return price_df

        elif type_tariff == 'price-rtp':
            print('Type of Tariff = price-rtp')
            # st, et = date_period
            # index = pd.date_range(st, et, freq=DEFAULT_DT)
            # return pd.DataFrame(data=raw_json_data, index=index)

        else:
            print('Type of Tariff is none of valid values')
            return None

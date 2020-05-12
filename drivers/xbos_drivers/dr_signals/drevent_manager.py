__author__ = 'Olivier Van Cutsem, Pranav Gupta'

import json
import os
import pytz
from datetime import timedelta
from dateutil.parser import parse

import electricitycostcalculator
import pandas as pd
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

    def add_default_dr_events(self, type_dr, dr_raw_data):
        """  Add default DR event to DREventManager.

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
            avail_events = [ev['data_dr'][(ev['data_dr'].index >= st) & (ev['data_dr'].index <= et)] for ev in
                            avail_events]

        return avail_events

    @staticmethod
    def convert_to_utc(date, timezone='US/Pacific'):
        local = pytz.timezone("US/Pacific")

        # NOTE: datetime module is possibly imported from electricitycostcalculator
        naive = datetime.strptime(date, '%Y-%m-%dT%H:%M:%S')

        local_dt = local.localize(naive, is_dst=None)
        utc_dt = local_dt.astimezone(pytz.utc)

        return utc_dt.strftime("%Y-%m-%dT%H:%M:%S")

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
            ret_dict['startdate'] = self.convert_to_utc(raw_data["start-date"])
            ret_dict['enddate'] = self.convert_to_utc(raw_data["end-date"])
            ret_dict['data_dr'] = self.get_df_tariff(raw_data["type"], (raw_data["start-date"], raw_data["end-date"]),
                                                     raw_data["data"])

        elif type_dr == 'dr-limit' or type_dr == 'dr-shed' or type_dr == 'dr-track':
            raw_data = raw_data["data"]
            ret_dict['type_dr'] = type_dr
            ret_dict['startdate'] = self.convert_to_utc(raw_data["start-date"])
            ret_dict['enddate'] = self.convert_to_utc(raw_data["end-date"])

            if type_dr == 'dr-track':
                st, et = parse(raw_data["start-date"]), parse(raw_data["end-date"])
                step = (et - st).total_seconds() / (60 * 15)
                if len(raw_data['profile']) == step:
                    data = {
                        'profile': raw_data['profile'],
                        'delta': raw_data['delta']
                    }
                    ret_dict['data_dr'] = data
                else:
                    raise ValueError('dr-track profile should contain the exact number of elements from start-date to '
                                     'end-date in 15min frequency')
            else:
                ret_dict['data_dr'] = raw_data['power']

        elif type_dr == 'dr-shift':
            raw_data = raw_data["data"]
            if (raw_data['end-date-take'] != raw_data['start-date-relax']) and (raw_data['end-date-relax'] != raw_data[
                'start-date-take']):
                raise ValueError('the dr-shift take and relax events should be contiguous, i.e. the end date of one '
                                 'should be equal to the start date of another')
            else:
                # This is for when get_available_events() filters by startdate and enddate
                st1, st2 = parse(raw_data["start-date-take"]), parse(raw_data["start-date-relax"])
                et1, et2 = parse(raw_data["end-date-take"]), parse(raw_data["end-date-relax"])
                ret_dict['startdate'] = raw_data["start-date-take"] if st1 < st2 else raw_data["start-date-relax"]
                ret_dict['enddate'] = raw_data["end-date-take"] if et1 > et2 else raw_data["end-date-relax"]

                start_date = {
                    'start-date-take': self.convert_to_utc(raw_data["start-date-take"]),
                    'start-date-relax': self.convert_to_utc(raw_data["start-date-relax"])
                }
                end_date = {
                    'end-date-take': self.convert_to_utc(raw_data["end-date-take"]),
                    'end-date-relax': self.convert_to_utc(raw_data["end-date-relax"])
                }
                power = {
                    'power-take': raw_data['power-take'],
                    'power-relax': raw_data['power-relax']
                }
                ret_dict['type_dr'] = type_dr
                ret_dict['startdate-take_relax'] = start_date
                ret_dict['enddate-take_relax'] = end_date
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
                    raise NotImplementedError('Only 15min frequency works for now.')
                    # print('price has hourly timestep...')
                    # timestep = TariffElemPeriod.HOURLY

                start_date_sig = parse(start_date)
                end_date_sig = parse(end_date)
                price_df, map = self.__tariff_manager.get_electricity_price((start_date_sig, end_date_sig), timestep)
                price_df['customer_demand_charge_tou'] = price_df['customer_demand_charge_tou'] + price_df['customer_demand_charge_season']
                price_df.index = price_df.tz_localize('US/Pacific').tz_convert('UTC')

            elif 'energy_prices' in raw_json_data and 'demand_prices' in raw_json_data:
                assert len(raw_json_data['energy_prices']) == len(raw_json_data['demand_prices'])
                st, et = parse(self.convert_to_utc(start_date)), parse(self.convert_to_utc(end_date))
                delta_sec = (et - st).total_seconds()

                if self.FORECAST_FREQUENCY == '15min':
                    step = timedelta(minutes=15)
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
                price_df.index = price_df.tz_localize('US/Pacific').tz_convert('UTC')
            else:
                raise KeyError('cannot find tariff-json or (energy_prices and demand_prices)')

            return price_df

        elif type_tariff == 'price-rtp':
            raise NotImplementedError('price-rtp')
            # st, et = date_period
            # index = pd.date_range(st, et, freq=DEFAULT_DT)
            # return pd.DataFrame(data=raw_json_data, index=index)

        else:
            print('Type of Tariff is none of valid values')
            return None

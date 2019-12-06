__author__ = 'Olivier Van Cutsem, Pranav Gupta'

import json
import os
import time
from datetime import datetime

import electricitycostcalculator
import pandas as pd
from dateutil.parser import parse
from electricitycostcalculator.cost_calculator.cost_calculator import CostCalculator
from electricitycostcalculator.cost_calculator.tariff_structure import *
from electricitycostcalculator.openei_tariff.openei_tariff_analyzer import *

costcalculator_path = os.path.dirname(electricitycostcalculator.__file__) + '/'
DEFAULT_DT = '1H'


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

    def __init__(self):

        # Dictionary of default events
        self.default_events = {}

        # List of custom DR events
        self.custom_dr_events = []

        # CostCalculator instance.
        self.__tariff_manager = CostCalculator()

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

        result['startdate'] = st
        result['enddate'] = et
        result['data_dr'] = self.get_df_tariff(self.default_events[type_dr]['type'], (st, et),
                                               self.default_events[type_dr]['data'])
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

        avail_events = [ev['data_dr'][(ev['data_dr'].index >= st) & (ev['data_dr'].index <= et)].to_json() for ev in
                      avail_events]

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

        if type_dr == 'dr_prices':
            ret_dict['type_dr'] = 'dr_prices'
            ret_dict['startdate'] = raw_data["start-date"]
            ret_dict['enddate'] = raw_data["end-date"]
            ret_dict['data_dr'] = self.get_df_tariff(raw_data["type"], (raw_data["start-date"], raw_data["end-date"]),
                                                     raw_data["data"])

        elif type_dr == 'dr_shed' or type_dr == 'dr_limit':
            print('DR Shed or DR Limit')
            # raw_data = raw_data["data"]
            # ret_dict['startdate'] = raw_data["start-date"]
            # ret_dict['enddate'] = raw_data["end-date"]
            # ret_dict['data_dr'] = self.get_df_powerconstraints([(raw_data["start-date"], raw_data["end-date"])],
            #                                                    [raw_data["power"]])

        elif type_dr == 'dr_shift':
            print('DR Shift')
            # raw_data = raw_data["data"]
            # ret_dict['startdate'] = raw_data["start-date-take"]
            # ret_dict['enddate'] = raw_data["end-date-relax"]
            # timeframe_list = [(raw_data["start-date-take"], raw_data["end-date-take"]),
            #                   (raw_data["start-date-relax"], raw_data["end-date-relax"])]
            # power_list = [raw_data["power-take"], raw_data["power-relax"]]
            # ret_dict['data_dr'] = self.get_df_powerconstraints(timeframe_list, power_list)

        elif type_dr == 'dr_track':
            print('DR Track')
            # raw_data = raw_data["data"]
            # ret_dict['startdate'] = raw_data["start-date"]
            # ret_dict['enddate'] = raw_data["end-date"]
            # ret_dict['data_dr'] = self.get_df_powersignal((raw_data["start-date"], raw_data["end-date"]),
            #                                               raw_data['profile'])

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
            # Init the CostCalculator with the tariff data
            tariff_data = OpenEI_tariff()
            tariff_data.read_from_json(costcalculator_path + raw_json_data['tariff-json'])

            # Now __tariff_manager has the blocks that defines the tariff
            tariff_struct_from_openei_data(tariff_data, self.__tariff_manager)

            # Get the price signal
            timestep = TariffElemPeriod.QUARTERLY

            start_date_sig = parse(start_date)
            end_date_sig = parse(end_date)
            price_df, map = self.__tariff_manager.get_electricity_price((start_date_sig, end_date_sig), timestep)

            return price_df

        elif type_tariff == 'price-rtp':
            print('Type of Tariff = price-rtp')
            # st, et = date_period
            # index = pd.date_range(st, et, freq=DEFAULT_DT)
            # return pd.DataFrame(data=raw_json_data, index=index)

        else:
            print('Type of Tariff is none of valid values')
            return None


"""
class DREventManager:

    def __init__(self):

        # # The amount of scheduled events since the beginning
        # self.__events_state = defaultdict(int)

        # This is an ordered list
        self.__scheduled_queue = []

        self.__tariff_manager = CostCalculator()

    # def get_scheduled_amount(self, type_dr):
    #     if type_dr not in list(self.__events_state.keys()): return 0
    #
    #     return self.__events_state[type_dr]
    #
    # def set_scheduled_amount(self, type_dr):
    #     self.__events_state[type_dr] += 1

    def add_available_event(self, ev):
        # TODO: insert the ev at the right place in the list
        self.__scheduled_queue.append(ev)

    def get_available_events(self, type_dr=None, timeframe=None):

        ret_sorted = self.__scheduled_queue

        # No specification: all the data
        if type_dr is None and timeframe is None:
            return [{'type': ev['type_dr'], 'data': ev['data_dr'].to_json()} for ev in ret_sorted if
                    ev['data_dr'] is not None]

        # Data type is specified
        if type_dr is not None:
            ret_sorted = [ev for ev in ret_sorted if ev['type_dr'] == type_dr]

        if timeframe is None:
            return [ev['data_dr'].to_json() for ev in ret_sorted]

        # Both timeframe and type of data are speficied
        # (1) get the signals overlapping with this timeframe (2) shorten the signal
        st, et = timeframe
        ret_sorted = [x for x in ret_sorted if (x['startdate'] is not None) and (x['enddate'] is not None)]
        ret_sorted = [x for x in ret_sorted if (st <= x['startdate'] <= et) or (st <= x['enddate'] <= et) or (
                x['startdate'] <= st and x['enddate'] >= et)]
        ret_sorted = [ev['data_dr'][(ev['data_dr'].index >= st) & (ev['data_dr'].index <= et)].to_json() for ev in
                      ret_sorted]

        return ret_sorted

    def decode_rawjson(self, type_dr, raw_data):
        notif_time = time.mktime(datetime.strptime(raw_data['notification-date'], "%Y-%m-%dT%H:%M:%S").timetuple())
        ret_dict = {'type_dr': type_dr, 'startdate': None, 'enddate': None, 'data_dr': None}

        if type_dr == 'dr_prices':
            ret_dict['startdate'] = raw_data["start-date"]
            ret_dict['enddate'] = raw_data["end-date"]
            ret_dict['data_dr'] = self.get_df_tariff(raw_data["type"], (raw_data["start-date"], raw_data["end-date"]),
                                                     raw_data["data"])
        elif type_dr == 'dr_shed' or type_dr == 'dr_limit':
            raw_data = raw_data["data"]
            ret_dict['startdate'] = raw_data["start-date"]
            ret_dict['enddate'] = raw_data["end-date"]
            ret_dict['data_dr'] = self.get_df_powerconstraints([(raw_data["start-date"], raw_data["end-date"])],
                                                               [raw_data["power"]])
        elif type_dr == 'dr_shift':
            raw_data = raw_data["data"]
            ret_dict['startdate'] = raw_data["start-date-take"]
            ret_dict['enddate'] = raw_data["end-date-relax"]
            timeframe_list = [(raw_data["start-date-take"], raw_data["end-date-take"]),
                              (raw_data["start-date-relax"], raw_data["end-date-relax"])]
            power_list = [raw_data["power-take"], raw_data["power-relax"]]
            ret_dict['data_dr'] = self.get_df_powerconstraints(timeframe_list, power_list)
        elif type_dr == 'dr_track':
            raw_data = raw_data["data"]
            ret_dict['startdate'] = raw_data["start-date"]
            ret_dict['enddate'] = raw_data["end-date"]
            ret_dict['data_dr'] = self.get_df_powersignal((raw_data["start-date"], raw_data["end-date"]),
                                                          raw_data['profile'])
        else:
            print('type_dr is none of valid DR Modes.')

        return notif_time, ret_dict

    def get_df_tariff(self, type_tariff, date_period, raw_json_data):
        " Return a Pandas dataframe of electricity prices

        Parameters
        ----------
        type_tariff     : str
            'price-rtp' or 'price-tou'
        date_period     : tuple
            (start_date, end_date)
        raw_json_data   : str
            Name of json file

        Returns
        -------
        pd.DataFrame
            Dataframe containing electricity prices.

        "
        start_date, end_date = date_period

        if type_tariff == 'price-tou':

            # Init the CostCalculator with the tariff data
            tariff_data = OpenEI_tariff()
            tariff_data.read_from_json(costcalculator_path + raw_json_data['tariff-json'])

            # Now __tariff_manager has the blocks that defines the tariff
            tariff_struct_from_openei_data(tariff_data, self.__tariff_manager)

            # PG: Changed from hourly to 15min
            # Get the price signal
            timestep = TariffElemPeriod.QUARTERLY

            start_date_sig = parse(start_date)
            end_date_sig = parse(end_date)
            price_df, map = self.__tariff_manager.get_electricity_price((start_date_sig, end_date_sig), timestep)

            return price_df

        elif type_tariff == 'price-rtp':
            st, et = date_period
            index = pd.date_range(st, et, freq=DEFAULT_DT)
            return pd.DataFrame(data=raw_json_data, index=index)

        else:
            return None

    def get_df_powerconstraints(self, l_timeframe, l_power_constraint):
        "
        Create and fill a Pandas dataframe with Power information between multiple timeframe
        :param timeframe: a list of tuple
        :param power_constraint: a list of power data
        :return:
        "

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

    def get_df_powersignal(self, timeframe, signal):
        "
        Create and fill a Pandas dataframe with Power information between multiple timeframe
        :param timeframe: a list of tuple
        :param power_constraint: a list of power data
        :return:
        "
        st, et = timeframe
        index = pd.date_range(st, et, freq=DEFAULT_DT)
        df = pd.DataFrame(data=signal, index=index, columns=['power'])

        return df
"""


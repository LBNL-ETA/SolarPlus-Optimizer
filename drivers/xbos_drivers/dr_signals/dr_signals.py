import argparse
import datetime
import json
import logging
import os
import time
from datetime import timedelta

import numpy as np
import pandas as pd
import yaml
from pyxbos import dr_signals_pb2
from pyxbos import xbos_pb2
from pyxbos.driver import *

from drevent_manager import DREventManager, read_from_json

# CONFIG VARIABLES
FORECAST_FREQUENCY = '15min'


class DRSignalsDriver(Driver):
    CUSTOM_EVENTS_FILE = 'dr_custom_events.json'
    DEFAULT_EVENTS_FILE = 'dr_default_events.json'
    NUM_CUSTOM_EVENTS = 0

    # Logging
    FORMAT = '%(asctime)-15s %(message)s'
    logging.basicConfig(format=FORMAT)
    logger = logging.getLogger('DR-SERVER')
    logger.setLevel(logging.INFO)

    # DR events information and state, to keep track of change and trigger new ones
    dr_manager = DREventManager(freq=FORECAST_FREQUENCY)

    @staticmethod
    def get_dr_mode(event_type):
        """ Get the DR Mode from the event type.

        Parameters
        ----------
        event_type  : str
            Types include "price-tou", "price-rtp"...

        Returns
        -------
        str
            DR Mode (one of [dr-prices, dr_shed, dr_limit, dr_shift, dr_track])
        """
        if event_type in ['price-tou', 'price-rtp']:
            return 'dr-prices'
        elif event_type == 'dr-limit':
            return 'dr-limit'
        else:
            raise ValueError('Event type does not correspond to a valid DR_MODE')

    @staticmethod
    def extract_json(json_result):
        """

        Parameters
        ----------
        json_result : json
            JSON from get_dr_signal()

        Returns
        -------
        list(list), list(list), datetime, datetime
            Price energy list, Price demand list, event start date, event end date
        """
        price_energy_list = []
        for timestamp, price in json_result['customer_energy_charge'].items():
            price_energy_list.append([timestamp, price])

        price_demand_list = []
        for timestamp, price in json_result['customer_demand_charge_tou'].items():
            price_demand_list.append([timestamp, price])

        assert len(price_energy_list) == len(price_demand_list)

        custom_st = datetime.datetime.fromtimestamp(int(price_energy_list[0][0]) / 1000)
        custom_et = datetime.datetime.fromtimestamp(int(price_energy_list[-1][0]) / 1000)

        return price_energy_list, price_demand_list, custom_st, custom_et

    @staticmethod
    def extract_dataframe(df):
        """ Convert price dataframe to list of list.

        Parameters
        ----------
        df  : pd.DataFrame()
            Dataframe from get_default_dr_signal()

        Returns
        -------
        list, list
            List of energy prices, list of demand prices
        """
        a = df.index.astype(np.int64).tolist()
        b = df['customer_energy_charge'].tolist()
        c = df['customer_demand_charge_tou'].tolist()
        list_energy = [list(x) for x in zip(a, b)]
        list_demand = [list(x) for x in zip(a, c)]
        return list_energy, list_demand

    def setup(self, cfg):
        self.base_resource = cfg['base_resource']

        # Keeps track of how further into the future should the forecast be
        # Value is in number of hours
        self.FORECAST_PERIOD = cfg['forecast_period']

        # Keeps track of the frequency of the forecast
        self.FORECAST_FREQUENCY = cfg['forecast_frequency']

        # Store the default values for min and max power
        self.default_pmin = cfg['pmin']
        self.default_pmax = cfg['pmax']

        # Init the scheduler state to keep track of the updates
        self.init_event_scheduler()

    def init_event_scheduler(self):
        """ Read the type of DR events from the file names.
        TODO: For more robustness, add a function that checks that there's only one default event for each DR mode.
        """
        if os.path.isfile(self.DEFAULT_EVENTS_FILE):
            default_events = read_from_json(self.DEFAULT_EVENTS_FILE)
            assert type(default_events) == list

            # Ensure each type has only one default event
            types = [event['type'] for event in default_events]
            assert (len(set(types)) == len(types))

            for event in default_events:
                self.dr_manager.add_default_dr_events(self.get_dr_mode(event['type']), event)
        else:
            raise FileNotFoundError(self.DEFAULT_EVENTS_FILE + ' file not found')

    def get_dr_signal(self, type_dr, start, end):
        """ Get information about a particular dr signal.

        Parameters
        ----------
        type_dr     : str
            Type of dr signal; choose one from ['dr-prices', 'dr_shed', 'dr_limit', 'dr_shift', 'dr_track']
        start       : str
            Start time; format - "YYYY-MM-DDTHH:MM:SS"
        end         : str
            End time; format - "YYYY-MM-DDTHH:MM:SS"

        Returns
        -------
        dict
            Json result

        """
        if (start is not None) and (end is not None):
            time_frame = (start, end)
            list_events = self.dr_manager.get_available_events(type_dr, time_frame)
            if not list_events:
                return None
            return json.dumps(list_events)
        else:
            raise ValueError('start and/or end is None.')

    def get_default_dr_signal(self, type_dr, start, end):
        """ Get information about default dr signal.

        Parameters
        ----------
        type_dr     : str
            Type of dr signal; choose one from ['dr-prices', 'dr_shed', 'dr_limit', 'dr_shift', 'dr_track']
        start       : str
            Start time; format - "YYYY-MM-DDTHH:MM:SS"
        end         : str
            End time; format - "YYYY-MM-DDTHH:MM:SS"

        Returns
        -------
        dict
            Json result

        """
        if (start is not None) and (end is not None):
            time_frame = (start, end)
            result = self.dr_manager.get_available_default_events(type_dr, time_frame)
            return result
        else:
            raise ValueError('start and/or end is None.')

    def update_dr_events(self):
        """ Read the files describing the DR events and add them internally.
        TODO: For more robustness, add no_overlapping_events() which ensures there are no custom events with
        overlapping time.
        """

        if os.path.isfile(self.CUSTOM_EVENTS_FILE):
            custom_events = read_from_json(self.CUSTOM_EVENTS_FILE)
            assert type(custom_events) == list

            # No new event has been added
            if len(custom_events) <= self.NUM_CUSTOM_EVENTS:
                print("No new event has been added.")

            # New event(s) has been added
            else:
                for i in range(len(custom_events) - self.NUM_CUSTOM_EVENTS):
                    self.dr_manager.add_dr_event(self.get_dr_mode(custom_events[i]['type']), custom_events[i])
                # TODO: Change this later to num_custom_events = len(dr_manager.custom_dr_events)
                self.NUM_CUSTOM_EVENTS = len(custom_events)
        else:
            raise FileNotFoundError(self.CUSTOM_EVENTS_FILE + ' file not found')

    def get_baseline(self):
        """ Returns current baseline.

        NOTE: Currently, this function returns a default of 100 kW.

        Returns
        -------
        float
            Baseline (unit = kW)
        """
        # TODO
        return 100

    def get_limit(self, curr_time, end_time):
        """ Gets max power.

        Parameters
        ----------
        curr_time   : datetime
            Current time.
        end_time    : datetime
            Forecast end time.

        Returns
        -------
        list(tuple, float)
            [(start_date, end_date), max_power]
        """
        result = self.get_dr_signal('dr-limit',
                                    curr_time.strftime('%Y-%m-%dT%H:%M:%SZ'),
                                    end_time.strftime('%Y-%m-%dT%H:%M:%SZ'))

        if not result:
            return None
        else:
            self.logger.info('dr-limit custom event')
            json_result = json.loads(result)
            json_result = json_result[0]

            pmax = json_result['data_dr']
            custom_st = datetime.datetime.strptime(json_result['startdate'], '%Y-%m-%dT%H:%M:%S')
            custom_et = datetime.datetime.strptime(json_result['enddate'], '%Y-%m-%dT%H:%M:%S')

            return [(custom_st, custom_et), pmax]

    def get_shed(self, curr_time, end_time):
        """ Gets max power.

        Parameters
        ----------
        curr_time   : datetime
            Current time.
        end_time    : datetime
            Forecast end time.

        Returns
        -------
        list(tuple, float)
            [(start_date, end_date), max_power]
        """
        baseline = self.get_baseline()
        result = self.get_dr_signal('dr-shed',
                                    curr_time.strftime('%Y-%m-%dT%H:%M:%SZ'),
                                    end_time.strftime('%Y-%m-%dT%H:%M:%SZ'))

        # Revert to default
        if not result:
            return None
        else:
            self.logger.info('dr-shed custom event')
            json_result = json.loads(result)
            json_result = json_result[0]

            pmax = json_result['data_dr']
            custom_st = datetime.datetime.strptime(json_result['startdate'], '%Y-%m-%dT%H:%M:%S')
            custom_et = datetime.datetime.strptime(json_result['enddate'], '%Y-%m-%dT%H:%M:%S')

            return [(custom_st, custom_et), baseline + pmax]

    def get_shift(self, curr_time, end_time):
        """ Gets max power.

        TODO: Error check to ensure that the power-take and power-relax are not overlapping

        Parameters
        ----------
        curr_time   : datetime
            Current time.
        end_time    : datetime
            Forecast end time.

        Returns
        -------
        list(list(tuple, float))
            [[(start_date, end_date), max_power]...] for power-take and power-relax.
        """
        baseline = self.get_baseline()
        result = self.get_dr_signal('dr-shed',
                                    curr_time.strftime('%Y-%m-%dT%H:%M:%SZ'),
                                    end_time.strftime('%Y-%m-%dT%H:%M:%SZ'))

        # Revert to default
        if not result:
            return None
        else:
            self.logger.info('dr-shift custom event')
            json_result = json.loads(result)
            json_result = json_result[0]

            ptake = json_result['data_dr']['power-take']
            prelax = json_result['data_dr']['power-relax']
            ptake_st = datetime.datetime.strptime(json_result['startdate']['start-date-take'], '%Y-%m-%dT%H:%M:%S')
            ptake_et = datetime.datetime.strptime(json_result['enddate']['end-date-take'], '%Y-%m-%dT%H:%M:%S')
            prelax_st = datetime.datetime.strptime(json_result['startdate']['start-date-relax'], '%Y-%m-%dT%H:%M:%S')
            prelax_et = datetime.datetime.strptime(json_result['enddate']['end-date-relax'], '%Y-%m-%dT%H:%M:%S')

            return [[(ptake_st, ptake_et), baseline + ptake], [(prelax_st, prelax_et), baseline + prelax]]

    def get_track(self, curr_time, end_time):
        """ Gets min and max power.

        Parameters
        ----------
        curr_time   : datetime
            Current time.
        end_time    : datetime
            Forecast end time.

        Returns
        -------
        list(tuple, list(float), float)
            [[(start_date, end_date), [power...], delta]
        """
        result = self.get_dr_signal('dr-shed',
                                    curr_time.strftime('%Y-%m-%dT%H:%M:%SZ'),
                                    end_time.strftime('%Y-%m-%dT%H:%M:%SZ'))

        # Revert to default
        if not result:
            return None
        else:
            self.logger.info('dr-track custom event')
            json_result = json.loads(result)
            json_result = json_result[0]

            power = json_result['data_dr']['profile']
            delta = json_result['data_dr']['delta']
            custom_st = datetime.datetime.strptime(json_result['startdate'], '%Y-%m-%dT%H:%M:%S')
            custom_et = datetime.datetime.strptime(json_result['enddate'], '%Y-%m-%dT%H:%M:%S')

            return [(custom_st, custom_et), power, delta]

    def get_power(self, curr_time, end_time):
        """ Get min_power and max_power from all dr power modes.

        Parameters
        ----------
        curr_time   : datetime
            Current time.
        end_time    : datetime
            Forecast end time.

        Returns
        -------
        list(list)
            [[timestamp, pmin, pmax]...]
        """
        result = []
        if self.FORECAST_FREQUENCY == '15min':
            step = timedelta(minutes=15)
        else:
            raise NotImplementedError('Forecast freq = 15min only.')

        limit_pmax = self.get_limit(curr_time, end_time)
        shed_pmax = self.get_shed(curr_time, end_time)
        shift_pmax = self.get_shift(curr_time, end_time)
        track_pmax = self.get_track(curr_time, end_time)

        if not track_pmax:
            if limit_pmax:
                diff = (limit_pmax[0][1] - limit_pmax[0][0]).total_seconds() / 60
                for date in (limit_pmax[0][0] + timedelta(minutes=n) for n in range(0, int(diff), 15)):
                    result.append([int(date.timestamp() * 10e6), self.default_pmin, limit_pmax[1]])
            if shed_pmax:
                diff = (shed_pmax[0][1] - shed_pmax[0][0]).total_seconds() / 60
                for date in (shed_pmax[0][0] + timedelta(minutes=n) for n in range(0, int(diff), 15)):
                    result.append([int(date.timestamp() * 10e6), self.default_pmin, shed_pmax[1]])
            if shift_pmax:
                diff = (shift_pmax[0][0][1] - shift_pmax[0][0][0]).total_seconds() / 60
                for date in (shift_pmax[0][0][0] + timedelta(minutes=n) for n in range(0, int(diff), 15)):
                    result.append([int(date.timestamp() * 10e6), self.default_pmin, shift_pmax[0][1]])

                diff = (shift_pmax[1][0][1] - shift_pmax[1][0][0]).total_seconds() / 60
                for date in (shift_pmax[1][0][0] + timedelta(minutes=n) for n in range(0, int(diff), 15)):
                    result.append([int(date.timestamp() * 10e6), self.default_pmin, shift_pmax[1][1]])

        else:  # If there's an event for dr-track, then ignore all other events
            diff = (track_pmax[0][1] - shed_pmax[0][0]).total_seconds() / 60
            pmin = track_pmax[1] - track_pmax[2]
            pmax = track_pmax[1] + track_pmax[2]
            for timestamp in (track_pmax[0][0] + timedelta(minutes=n) for n in range(0, int(diff), 15)):
                result.append([timestamp, pmin, pmax])

        return result

    def get_price(self, curr_time, end_time):
        """ Gets the energy and demand price forecast.

        Parameters
        ----------
        curr_time   : datetime
            Current time.
        end_time    : datetime
            Forecast end time.

        Returns
        -------
        list(list), list(list)
            [[timestamp, energy_price]...], [[timestamp, demand_price]...]
        """
        curr_time_formatted = curr_time.strftime('%Y-%m-%dT%H:%M:%SZ')
        end_time_formatted = end_time.strftime('%Y-%m-%dT%H:%M:%SZ')

        result = self.get_dr_signal('dr-prices', curr_time_formatted, end_time_formatted)

        # Revert to default event
        if not result:
            self.logger.info('dr-price default event')
            default_result = self.get_default_dr_signal('dr-prices', curr_time_formatted, end_time_formatted)
            final_energy, final_demand = self.extract_dataframe(default_result['data_dr'])

        # Custom event
        else:
            self.logger.info('dr-price custom event')
            json_result = json.loads(result)
            json_result = json.loads(json_result[0])

            final_energy, final_demand, custom_st, custom_et = self.extract_json(json_result)

            if custom_st > curr_time:
                default_result = self.get_default_dr_signal('dr-prices',
                                                            curr_time_formatted,
                                                            custom_st.strftime('%Y-%m-%dT%H:%M:%SZ'))
                energy_price1, demand_price2 = self.extract_dataframe(default_result['data_dr'])
                final_energy = energy_price1 + final_energy
                final_demand = demand_price2 + final_demand
            if custom_et < end_time:
                default_result = self.get_default_dr_signal('dr-prices',
                                                            custom_et.strftime('%Y-%m-%dT%H:%M:%SZ'),
                                                            end_time_formatted)
                energy_price2, demand_price2 = self.extract_dataframe(default_result['data_dr'])
                final_energy = final_energy + energy_price2
                final_demand = final_demand + demand_price2

        return final_energy, final_demand

    def read(self, requestid=None):

        # Read the events list, see if there are new ones and add them
        self.logger.info("Updating the event list")

        # Checks if new event(s) have been added
        self.update_dr_events()

        # CHECK: Time now should be in local time or UTC?
        curr_time = datetime.datetime.now()
        end_time = curr_time + timedelta(hours=self.FORECAST_PERIOD)

        price_energy, price_demand = self.get_price(curr_time, end_time)
        power = self.get_power(curr_time, end_time)

        df1 = pd.DataFrame(price_energy, columns=['timestamp', 'energy'])
        df2 = pd.DataFrame(price_demand, columns=['timestamp', 'demand'])
        df1.set_index('timestamp', inplace=True)
        df2.set_index('timestamp', inplace=True)
        df = df1.join(df2, how='outer')

        df3 = pd.DataFrame(power, columns=['timestamp', 'pmin', 'pmax'])
        df3.set_index('timestamp', inplace=True)
        df = df.join(df3, how='outer')
        df['pmin'].fillna(1, inplace=True)
        df['pmax'].fillna(23, inplace=True)

        msg_list = []
        for index, row in df.iterrows():
            msg = dr_signals_pb2.DRSignalsPrediction.Prediction(
                forecast_time=int(index),
                price_energy=types.Double(value=row['energy']),
                price_demand=types.Double(value=row['demand']),
                pmin=types.Double(value=row['pmin']),
                pmax=types.Double(value=row['pmax'])
            )
            msg_list.append(msg)

        message = xbos_pb2.XBOS(
            drsigpred=dr_signals_pb2.DRSignalsPrediction(
                time=int(time.time() * 1e9),
                signal_type=0,
                predictions=msg_list
            )
        )
        self.report('resource1', message)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('config_file', help='config file')

    args = parser.parse_args()
    config_file = args.config_file

    with open(config_file) as f:
        driverConfig = yaml.safe_load(f)

    logging.basicConfig(level="INFO", format='%(asctime)s - %(name)s - %(message)s')
    dr_signal_driver = DRSignalsDriver(driverConfig)
    dr_signal_driver.begin()

import argparse
import datetime
import json
import logging
import os
import time
from datetime import timedelta

import numpy as np
import yaml
from pyxbos import dr_signals_pb2
from pyxbos import xbos_pb2
from pyxbos.driver import *

from drevent_manager import DREventManager, read_from_json


# NOTE: Make pmin and pmax as config parameters
# NOTE: pmin and pmax will be taken from dr_limit, dr_shed...
# Push all the files for this driver in SolarPlusOptimizer


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
    dr_manager = DREventManager()

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

        # Init the scheduler state to keep track of the updates
        self.init_event_scheduler()

    def init_event_scheduler(self):
        """ Read the type of DR events from the file names. """
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
        """ Read the files describing the DR events and add them internally. """

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

        # Revert to default
        if not result:
            print("Default event...")
            default_result = self.get_default_dr_signal('dr-prices', curr_time_formatted, end_time_formatted)
            final_energy, final_demand = self.extract_dataframe(default_result['data_dr'])

        # Custom event
        else:
            print('Custom event...')
            json_result = json.loads(result)
            json_result = json.loads(json_result[0])

            price_energy_list, price_demand_list, custom_st, custom_et = self.extract_json(json_result)

            # Case 1: custom event is happening for the next FORECAST_PERIOD hours
            # ---------| |---------
            if (custom_st >= curr_time) and (custom_et <= end_time):
                final_energy = price_energy_list
                final_demand = price_demand_list

            # Case 2: use default for x hours and then custom event
            # --------- | --------- |
            if custom_st >= curr_time:
                default_result = self.get_default_dr_signal('dr-prices', curr_time_formatted,
                                                       custom_st.strftime('%Y-%m-%dT%H:%M:%SZ'))
                list_energy, list_demand = self.extract_dataframe(default_result['data_dr'])
                final_energy = list_energy + price_energy_list
                final_demand = list_demand + price_demand_list

            # Case 3: use custom event for x hours and then default
            # | --------- | ---------
            if custom_et <= end_time:
                default_result = self.get_default_dr_signal('dr-prices', custom_et.strftime('%Y-%m-%dT%H:%M:%SZ'),
                                                            end_time_formatted)
                list_energy, list_demand = self.extract_dataframe(default_result['data_dr'])
                final_energy = price_energy_list + list_energy
                final_demand = price_demand_list + list_demand

        return final_energy, final_demand

    def get_limit(self, curr_time, end_time):
        """ Gets max power.

        TODO: REMOVE DEFAULT VALUES (USE DEFAULT PMAX VALUE FROM CONFIG FILE)

        Parameters
        ----------
        curr_time   : datetime
            Current time.
        end_time    : datetime
            Forecast end time.

        Returns
        -------
        list(list)
            [[start_time, end_time, pmax]]
        """
        final_pmax = []
        curr_time_formatted = curr_time.strftime('%Y-%m-%dT%H:%M:%SZ')
        end_time_formatted = end_time.strftime('%Y-%m-%dT%H:%M:%SZ')

        result = self.get_dr_signal('dr-limit', curr_time_formatted, end_time_formatted)
        print('dr-limit result: ', result)

        # Revert to default
        if not result:
            print("Default event...")
            # default_result = self.get_default_dr_signal('dr-limit', curr_time_formatted, end_time_formatted)
            # final_pmax = default_result['data_dr']['power']
        else:
            print('Custom event...')
            json_result = json.loads(result)
            json_result = json_result[0]

            custom_pmax = json_result['data_dr']['power']
            custom_st = datetime.datetime.strptime(json_result['startdate'], '%Y-%m-%dT%H:%M:%S')
            custom_et = datetime.datetime.strptime(json_result['enddate'], '%Y-%m-%dT%H:%M:%S')

            # Case 1: custom event is happening for the next FORECAST_PERIOD hours
            # ---------| |---------
            if (custom_st >= curr_time) and (custom_et <= end_time):
                print('case 1')
                final_pmax.append([custom_st, custom_et, custom_pmax])

            # Case 2: use default for x hours and then custom event
            # --------- | --------- |
            if custom_st >= curr_time:
                print('case 2')
                # default_result = self.get_default_dr_signal('dr-limit', curr_time_formatted,
                #                                             custom_st.strftime('%Y-%m-%dT%H:%M:%SZ'))
                # default_pmax = default_result['data_dr']['power']
                # final_pmax.append([curr_time, custom_st, default_pmax])
                final_pmax.append([custom_st, end_time, custom_pmax])

            # Case 3: use custom event for x hours and then default
            # | --------- | ---------
            if custom_et <= end_time:
                print('case 3')
                # default_result = self.get_default_dr_signal('dr-limit', custom_et.strftime('%Y-%m-%dT%H:%M:%SZ'),
                #                                             end_time_formatted)
                # print('default: result: ', default_result)
                # default_pmax = default_result['data_dr']['power']
                final_pmax.append([custom_st, custom_et, custom_pmax])
                # final_pmax.append([custom_et, end_time, default_pmax])

        return final_pmax

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
        list(list)
            [[start_time, end_time, pmax]]
        """
        final_pmax = []
        curr_time_formatted = curr_time.strftime('%Y-%m-%dT%H:%M:%SZ')
        end_time_formatted = end_time.strftime('%Y-%m-%dT%H:%M:%SZ')

        # TODO: Calculate baseline here
        # baseline =

        result = self.get_dr_signal('dr-shed', curr_time_formatted, end_time_formatted)
        print('dr-shed result: ', result)

        # Revert to default
        if not result:
            print("Default event...")
        else:
            print('Custom event...')
            json_result = json.loads(result)
            json_result = json_result[0]

            custom_pmax = json_result['data_dr']['power']
            custom_st = datetime.datetime.strptime(json_result['startdate'], '%Y-%m-%dT%H:%M:%S')
            custom_et = datetime.datetime.strptime(json_result['enddate'], '%Y-%m-%dT%H:%M:%S')

            # Case 1: custom event is happening for the next FORECAST_PERIOD hours
            # ---------| |---------
            if (custom_st >= curr_time) and (custom_et <= end_time):
                print('case 1')
                final_pmax.append([custom_st, custom_et, custom_pmax])

            # Case 2: use default for x hours and then custom event
            # --------- | --------- |
            if custom_st >= curr_time:
                print('case 2')
                # default_result = self.get_default_dr_signal('dr-shed', curr_time_formatted,
                #                                             custom_st.strftime('%Y-%m-%dT%H:%M:%SZ'))
                # default_pmax = default_result['data_dr']['power']
                # final_pmax.append([curr_time, custom_st, default_pmax])

                # Uncomment below line once the code for baseline has been written
                # final_pmax.append([custom_st, end_time, baseline + custom_pmax])

            # Case 3: use custom event for x hours and then default
            # | --------- | ---------
            if custom_et <= end_time:
                print('case 3')
                # default_result = self.get_default_dr_signal('dr-shed', custom_et.strftime('%Y-%m-%dT%H:%M:%SZ'),
                #                                             end_time_formatted)
                # print('default: result: ', default_result)
                # default_pmax = default_result['data_dr']['power']

                # Uncomment below line once the code for baseline has been written
                # final_pmax.append([custom_st, custom_et, baseline + custom_pmax])

                # final_pmax.append([custom_et, end_time, default_pmax])

        return final_pmax

    # def get_shift(self, curr_time, end_time):
    #     """ Gets min and max power.
    #
    #     TODO: Error check to ensure that the power-take and power-relax are contiguous
    #
    #     Parameters
    #     ----------
    #     curr_time   : datetime
    #         Current time.
    #     end_time    : datetime
    #         Forecast end time.
    #
    #     Returns
    #     -------
    #     list(list)
    #         [[start_time, end_time, pmax]...]
    #     """
    #     final_pmax = []
    #     curr_time_formatted = curr_time.strftime('%Y-%m-%dT%H:%M:%SZ')
    #     end_time_formatted = end_time.strftime('%Y-%m-%dT%H:%M:%SZ')
    #
    #     # TODO: Calculate baseline here
    #     # baseline =
    #
    #     result = self.get_dr_signal('dr-shift', curr_time_formatted, end_time_formatted)
    #     print('dr-shift result: ', result)
    #
    #     # Revert to default
    #     if not result:
    #         print("Default event...")
    #     else:
    #         print('Custom event...')
    #         json_result = json.loads(result)
    #         json_result = json_result[0]
    #
    #         custom_ptake = json_result['data_dr']['power-take']
    #         custom_prelax = json_result['data_dr']['power-relax']
    #         custom_st = datetime.datetime.strptime(json_result['startdate'], '%Y-%m-%dT%H:%M:%S')
    #         custom_et = datetime.datetime.strptime(json_result['enddate'], '%Y-%m-%dT%H:%M:%S')
    #
    #         # # Case 1: custom event is happening for the next FORECAST_PERIOD hours
    #         # # ---------| |---------
    #         # if (custom_st >= curr_time) and (custom_et <= end_time):
    #         #     print('case 1')
    #         #
    #         # # Case 2: use default for x hours and then custom event
    #         # # --------- | --------- |
    #         # if custom_st >= curr_time:
    #         #     print('case 2')
    #         #
    #         # # Case 3: use custom event for x hours and then default
    #         # # | --------- | ---------
    #         # if custom_et <= end_time:
    #         #     print('case 3')
    #
    #     return final_pmax

    # def get_track(self, curr_time, end_time):
    #     # TODO
    #     """ Gets max power.
    #
    #     Parameters
    #     ----------
    #     curr_time   : datetime
    #         Current time.
    #     end_time    : datetime
    #         Forecast end time.
    #
    #     Returns
    #     -------
    #     list(list(list))
    #         [[start_time, end_time, [pmax...]]]
    #     """
    #     final_pmax = []
    #     curr_time_formatted = curr_time.strftime('%Y-%m-%dT%H:%M:%SZ')
    #     end_time_formatted = end_time.strftime('%Y-%m-%dT%H:%M:%SZ')
    #
    #     # TODO: Calculate baseline here
    #     # baseline =
    #
    #     result = self.get_dr_signal('dr-shed', curr_time_formatted, end_time_formatted)
    #     print('dr-shed result: ', result)
    #
    #     # Revert to default
    #     if not result:
    #         print("Default event...")
    #     else:
    #         print('Custom event...')
    #         json_result = json.loads(result)
    #         json_result = json_result[0]
    #
    #         custom_pmax = json_result['data_dr']['profile']
    #         custom_st = datetime.datetime.strptime(json_result['startdate'], '%Y-%m-%dT%H:%M:%S')
    #         custom_et = datetime.datetime.strptime(json_result['enddate'], '%Y-%m-%dT%H:%M:%S')
    #
    #         # Case 1: custom event is happening for the next FORECAST_PERIOD hours
    #         # ---------| |---------
    #         if (custom_st >= curr_time) and (custom_et <= end_time):
    #             print('case 1')
    #             final_pmax.append([custom_st, custom_et, custom_pmax])
    #
    #         # Case 2: use default for x hours and then custom event
    #         # --------- | --------- |
    #         if custom_st >= curr_time:
    #             print('case 2')
    #             # default_result = self.get_default_dr_signal('dr-shed', curr_time_formatted,
    #             #                                             custom_st.strftime('%Y-%m-%dT%H:%M:%SZ'))
    #             # default_pmax = default_result['data_dr']['power']
    #             # final_pmax.append([curr_time, custom_st, default_pmax])
    #
    #             # Uncomment below line once the code for baseline has been written
    #             # final_pmax.append([custom_st, end_time, baseline + custom_pmax])
    #
    #         # Case 3: use custom event for x hours and then default
    #         # | --------- | ---------
    #         if custom_et <= end_time:
    #             print('case 3')
    #             # default_result = self.get_default_dr_signal('dr-shed', custom_et.strftime('%Y-%m-%dT%H:%M:%SZ'),
    #             #                                             end_time_formatted)
    #             # print('default: result: ', default_result)
    #             # default_pmax = default_result['data_dr']['power']
    #
    #             # Uncomment below line once the code for baseline has been written
    #             # final_pmax.append([custom_st, custom_et, baseline + custom_pmax])
    #
    #             # final_pmax.append([custom_et, end_time, default_pmax])
    #
    #     return final_pmax

    def read(self, requestid=None):

        # Read the events list, check if there are new ones and add them
        self.logger.info("Updating the event list")

        # Check if new event(s) has been added
        self.update_dr_events()

        # CHECK: Time now should be in local time or UTC?
        curr_time = datetime.datetime.now()
        end_time = curr_time + timedelta(hours=self.FORECAST_PERIOD)

        price_energy, price_demand = self.get_price(curr_time, end_time)
        limit_pmax = self.get_limit(curr_time, end_time)
        shed_pmax = self.get_shed(curr_time, end_time)
        shift_pmax = self.get_shift(curr_time, end_time)
        track_pmax = self.get_track(curr_time, end_time)

        # pmin = config['pmin']
        if not track_pmax:
            pmax = min(limit_pmax, shed_pmax, shift_pmax)
        else:
            # use track_pmax

        """
        msg_list = []
        for i in range(len(final_demand)):
            assert final_demand[i][0] == final_energy[i][0]
            msg = dr_signals_pb2.DRSignalsPrediction.Prediction(
                forecast_time=int(final_energy[i][0]),
                price_energy=types.Double(value=final_energy[i][1]),
                price_demand=types.Double(value=final_demand[i][1]),
                pmin=types.Double(value=0),
                pmax=types.Double(value=999999)
            )
            msg_list.append(msg)

        message = xbos_pb2.XBOS(
            drsigpred=dr_signals_pb2.DRSignalsPrediction(
                time=int(time.time() * 1e9),
                signal_type=0,  # 0 signifies price
                predictions=msg_list
            )
        )

        self.report('resource1', message)
        """


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

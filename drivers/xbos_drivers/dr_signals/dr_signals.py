import argparse
import datetime
import logging
import os
from datetime import timedelta

import pandas as pd
import yaml
from drevent_manager import DREventManager, read_from_json
from pyxbos import constraints_forecast_pb2
from pyxbos import dr_signals_pb2
from pyxbos import xbos_pb2
from pyxbos.driver import *
from pyxbos.process import XBOSProcess, b64decode, schedule, run_loop

""" NOTE,
1. Current assumption of driver includes that no two custom events have overlapping times. 
2. Times in the json files are in local time.
3. dr-shed and dr-shift events are not published because the baseline hasn't been implemented yet.
"""

# Global variable
FORECAST_FREQUENCY = '15min'


class DRSignalsDriver(XBOSProcess):

    def __init__(self, cfg):
        """ Constructor.

        Parameters
        ----------
        cfg     : str
            Configuration file.
        """
        super().__init__(cfg)

        self.CUSTOM_EVENTS_FILE = 'dr_custom_events.json'
        self.DEFAULT_EVENTS_FILE = 'dr_default_events.json'
        self.NUM_CUSTOM_EVENTS = 0

        self.dr_mode_signal_type_mapping = {
            'none': 0,
            'dr-limit': 1,
            'dr-shed': 2,
            'dr-shift': 3,
            'dr-track': 4
        }

        # Logging
        self.FORMAT = '%(asctime)-15s %(message)s'
        logging.basicConfig(format=self.FORMAT)
        self.logger = logging.getLogger('DR-SERVER')
        self.logger.setLevel(logging.INFO)

        # DR events information and state, to keep track of change and trigger new ones
        self.dr_manager = DREventManager(freq=FORECAST_FREQUENCY)

        self.base_resource1 = cfg['base_resource1']  # dr_signals
        self.base_resource2 = cfg['base_resource2']  # constraints (pmin and pmax)
        self.namespace = b64decode(cfg['namespace'])
 
        # Keeps track of how further into the future should the forecast be
        # Value is in number of hours
        self.FORECAST_PERIOD = cfg['forecast_period']

        # Store the default values for min and max power
        self.default_pmin = cfg['pmin']
        self.default_pmax = cfg['pmax']

        # Publishing rate
        self._rate = cfg['rate']

        # Get DR Signals every _rate seconds and publish
        schedule(self.call_periodic(self._rate, self.read, runfirst=True))

        # Init the scheduler state to keep track of the updates
        self.init_event_scheduler()

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
        elif event_type in ['dr-limit', "dr-shed", "dr-shift", "dr-track"]:
            return event_type
        else:
            raise ValueError('Event type does not correspond to a valid DR_MODE')

    def init_event_scheduler(self):
        """ Populate DR Manager with default events. Current implementation includes dr-prices only.
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
            result = self.dr_manager.get_available_events(type_dr, time_frame)
            if not result:
                return None
            return result
        else:
            raise ValueError('start and/or end is None.')

    def get_default_dr_signal(self, type_dr, start, end):
        """ Get information about a default dr signal. Current implementation includes dr-prices only.

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
        """ Populate DR Manager with any new events added to json file.
        TODO: For more robustness, add no_overlapping_events() which ensures there are no custom events with
        overlapping times.
        """

        if os.path.isfile(self.CUSTOM_EVENTS_FILE):
            custom_events = read_from_json(self.CUSTOM_EVENTS_FILE)
            assert type(custom_events) == list

            # No new event has been added
            if len(custom_events) <= self.NUM_CUSTOM_EVENTS:
                self.logger.info("No new event has been added.")

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

        # TODO: Subscribe to topic that has baseline
        NOTE: Currently, this function returns a default of 100 kW.

        Returns
        -------
        float
            Baseline (unit = kW)
        """
        return 100

    def get_limit(self, curr_time, end_time):
        """ Gets dr-limit power.

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
                                    curr_time.strftime('%Y-%m-%dT%H:%M:%S'),
                                    end_time.strftime('%Y-%m-%dT%H:%M:%S'))

        if not result:
            return None
        else:
            self.logger.info('dr-limit custom event')
            pmax = result[0]['data_dr']
            custom_st = datetime.datetime.strptime(result[0]['startdate'], '%Y-%m-%dT%H:%M:%S')
            custom_et = datetime.datetime.strptime(result[0]['enddate'], '%Y-%m-%dT%H:%M:%S')

            return [(custom_st, custom_et), pmax]

    def get_shed(self, curr_time, end_time):
        """ Gets dr-shed power.

        Parameters
        ----------
        curr_time   : datetime
            Current time.
        end_time    : datetime
            Forecast end time.

        Returns
        -------
        list(tuple, float)
            [(start_date, end_date), power]
        """
        baseline = self.get_baseline()
        result = self.get_dr_signal('dr-shed',
                                    curr_time.strftime('%Y-%m-%dT%H:%M:%S'),
                                    end_time.strftime('%Y-%m-%dT%H:%M:%S'))

        # Revert to default
        if not result:
            return None
        else:
            self.logger.info('dr-shed custom event')
            pmax = result[0]['data_dr']
            custom_st = datetime.datetime.strptime(result[0]['startdate'], '%Y-%m-%dT%H:%M:%S')
            custom_et = datetime.datetime.strptime(result[0]['enddate'], '%Y-%m-%dT%H:%M:%S')

            return [(custom_st, custom_et), baseline + pmax]

    def get_shift(self, curr_time, end_time):
        """ Gets dr-shift power.

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
        result = self.get_dr_signal('dr-shift',
                                    curr_time.strftime('%Y-%m-%dT%H:%M:%S'),
                                    end_time.strftime('%Y-%m-%dT%H:%M:%S'))

        # Revert to default
        if not result:
            return None
        else:
            self.logger.info('dr-shift custom event')
            ptake = result[0]['data_dr']['power-take']
            prelax = result[0]['data_dr']['power-relax']
            ptake_st = datetime.datetime.strptime(result[0]['startdate-take_relax']['start-date-take'],
                                                  '%Y-%m-%dT%H:%M:%S')
            ptake_et = datetime.datetime.strptime(result[0]['enddate-take_relax']['end-date-take'], '%Y-%m-%dT%H:%M:%S')
            prelax_st = datetime.datetime.strptime(result[0]['startdate-take_relax']['start-date-relax'],
                                                   '%Y-%m-%dT%H:%M:%S')
            prelax_et = datetime.datetime.strptime(result[0]['enddate-take_relax']['end-date-relax'],
                                                   '%Y-%m-%dT%H:%M:%S')

            return [[(ptake_st, ptake_et), baseline + ptake], [(prelax_st, prelax_et), baseline + prelax]]

    def get_track(self, curr_time, end_time):
        """ Gets dr-track power.

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
        result = self.get_dr_signal('dr-track',
                                    curr_time.strftime('%Y-%m-%dT%H:%M:%S'),
                                    end_time.strftime('%Y-%m-%dT%H:%M:%S'))

        # Revert to default
        if not result:
            return None
        else:
            self.logger.info('dr-track custom event')
            power = result[0]['data_dr']['profile']
            delta = result[0]['data_dr']['delta']
            custom_st = datetime.datetime.strptime(result[0]['startdate'], '%Y-%m-%dT%H:%M:%S')
            custom_et = datetime.datetime.strptime(result[0]['enddate'], '%Y-%m-%dT%H:%M:%S')

            return [(custom_st, custom_et), power, delta]

    def get_power(self, curr_time, end_time):
        """ Get min_power and max_power from all dr power modes.

        Note: power is the same as pmax in all cases except dr-track where 'power' differs from 'pmin' and 'pmax'
        'power' = dr-track profile in json file, 'pmax' and 'pmin' are profile +- delta

        Parameters
        ----------
        curr_time   : datetime
            Current time.
        end_time    : datetime
            Forecast end time.

        Returns
        -------
        pd.DataFrame()
            Dataframe containing timestamp, power, pmin, pmax and dr-mode.
        """
        result = []
        if FORECAST_FREQUENCY == '15min':
            step = timedelta(minutes=15)
        else:
            raise NotImplementedError('Forecast freq = 15min only.')

        limit_pmax = self.get_limit(curr_time, end_time)
        shed_pmax = self.get_shed(curr_time, end_time)
        shift_pmax = self.get_shift(curr_time, end_time)
        track_pmax = self.get_track(curr_time, end_time)

        # The below code works on the assumption that no custom events have overlapping times.

        if limit_pmax:
            diff = (limit_pmax[0][1] - limit_pmax[0][0]).total_seconds() / 60
            for date in (limit_pmax[0][0] + timedelta(minutes=n) for n in range(0, int(diff), 15)):
                result.append([date, limit_pmax[1], self.default_pmin, limit_pmax[1], 'dr-limit'])
        if shed_pmax:
            diff = (shed_pmax[0][1] - shed_pmax[0][0]).total_seconds() / 60
            for date in (shed_pmax[0][0] + timedelta(minutes=n) for n in range(0, int(diff), 15)):
                result.append([date, shed_pmax[1], self.default_pmin, shed_pmax[1], 'dr-shed'])
        if shift_pmax:
            diff = (shift_pmax[0][0][1] - shift_pmax[0][0][0]).total_seconds() / 60
            for date in (shift_pmax[0][0][0] + timedelta(minutes=n) for n in range(0, int(diff), 15)):
                result.append([date, shift_pmax[0][1], self.default_pmin, shift_pmax[0][1], 'dr-shift'])

            diff = (shift_pmax[1][0][1] - shift_pmax[1][0][0]).total_seconds() / 60
            for date in (shift_pmax[1][0][0] + timedelta(minutes=n) for n in range(0, int(diff), 15)):
                result.append([date, shift_pmax[1][1], self.default_pmin, shift_pmax[1][1], 'dr-shift'])
        if track_pmax:
            diff = (track_pmax[0][1] - track_pmax[0][0]).total_seconds() / 60
            pmin = [x - track_pmax[2] for x in track_pmax[1]]
            pmax = [x + track_pmax[2] for x in track_pmax[1]]
            for i, date in enumerate(track_pmax[0][0] + timedelta(minutes=n) for n in range(0, int(diff), 15)):
                result.append([date, track_pmax[1][i], pmin[i], pmax[i], 'dr-track'])

        power_df = pd.DataFrame(result, columns=['timestamp', 'power', 'pmin', 'pmax', 'dr-mode'])
        power_df.set_index('timestamp', inplace=True)
        return power_df

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
        pd.DataFrame()
            Dataframe containing energy and demand prices.
        """
        curr_time_formatted = curr_time.strftime('%Y-%m-%dT%H:%M:%S')
        end_time_formatted = end_time.strftime('%Y-%m-%dT%H:%M:%S')

        result = self.get_dr_signal('dr-prices', curr_time_formatted, end_time_formatted)

        # Revert to default event
        if not result:
            self.logger.info('dr-price default event')
            price_df = self.get_default_dr_signal('dr-prices', curr_time_formatted, end_time_formatted)
            return price_df['data_dr'][['customer_energy_charge', 'customer_demand_charge_tou']]

        # Custom event
        else:
            self.logger.info('dr-price custom event')

            # custom_st(et) are pandas.Timestamp
            custom_st, custom_et = result[0].index[0], result[0].index[-1]
            price_df = result[0]

            if custom_st > curr_time:
                default_result = self.get_default_dr_signal('dr-prices',
                                                            curr_time_formatted,
                                                            custom_st.strftime('%Y-%m-%dT%H:%M:%S'))
                price_df = pd.concat([default_result['data_dr'], price_df])
            if custom_et < end_time:
                default_result = self.get_default_dr_signal('dr-prices',
                                                            custom_et.strftime('%Y-%m-%dT%H:%M:%S'),
                                                            end_time_formatted)
                price_df = pd.concat([price_df, default_result['data_dr']])

        return price_df[['customer_energy_charge', 'customer_demand_charge_tou']]

    def extract_df_row(self, row):
        """ Extract row into array of results for publishing message on wavemq.

        Parameters
        ----------
        row     : dict
            Dataframe row.

        Returns
        -------
        list
            List containing the proto field data in the correct order.
        """
        result = []

        result.append(row['customer_energy_charge'])
        result.append(row['customer_demand_charge_tou'])
        result.append(self.dr_mode_signal_type_mapping[row['dr-mode']])

        if row['dr-mode'] == 'none':
            result += [-1, -1, -1, -1]
        elif row['dr-mode'] == 'dr-limit':
            result += [row['power'], -1, -1, -1]
        elif row['dr-mode'] == 'dr-shed':
            result += [-1, row['power'], -1, -1]
        elif row['dr-mode'] == 'dr-shift':
            result += [-1, -1, row['power'], -1]
        elif row['dr-mode'] == 'dr-track':
            result += [-1, -1, -1, row['power']]
        else:
            raise ValueError

        return result

    async def read(self):

        # Read the events list, see if there are new ones and add them
        self.logger.info("Updating the event list")

        # Checks if new event(s) have been added
        self.update_dr_events()

        curr_time = datetime.datetime.now()
        end_time = curr_time + timedelta(hours=self.FORECAST_PERIOD)

        df_price = self.get_price(curr_time, end_time)
        df_power = self.get_power(curr_time, end_time)

        df = df_price.join(df_power, how='outer')
        df.index = pd.to_datetime(df.index)
        df['pmin'].fillna(self.default_pmin, inplace=True)
        df['pmax'].fillna(self.default_pmax, inplace=True)
        df['dr-mode'].fillna('none', inplace=True)
        df.index = df.index.round(FORECAST_FREQUENCY)

        tim = int(time.time() * 1e9)

        # Publish to dr_signals
        # Uncomment once self.get_baseline() works
        msg_list1 = []
        for index, row in df.iterrows():
            result = self.extract_df_row(row)
            if result[2] == 4: # track event
                msg = dr_signals_pb2.DRSignalsPrediction.Prediction(
                    forecast_time=int(index.timestamp()),
                    price_energy=types.Double(value=result[0]),
                    price_demand=types.Double(value=result[1]),
                    signal_type=types.Uint64(value=result[2]),  # 0 - none, 1 - limit, 2 - shed, 3 - shift, 4 - track
                    power_track=types.Double(value=result[6])
                )
            elif result[2] == 0: # no event
                msg = dr_signals_pb2.DRSignalsPrediction.Prediction(
                    forecast_time=int(index.timestamp()),
                    price_energy=types.Double(value=result[0]),
                    price_demand=types.Double(value=result[1]),
                    signal_type=types.Uint64(value=result[2]),  # 0 - none, 1 - limit, 2 - shed, 3 - shift, 4 - track
                )
            else:
                msg = dr_signals_pb2.DRSignalsPrediction.Prediction(
                    forecast_time=int(index.timestamp()),
                    price_energy=types.Double(value=result[0]),
                    price_demand=types.Double(value=result[1]),
                    signal_type=types.Uint64(value=result[2]),  # 0 - none, 1 - limit, 2 - shed, 3 - shift, 4 - track
                    power_limit=types.Double(value=result[3]),
                    # power_shed=types.Double(value=result[4]),
                    # power_shift=types.Double(value=result[5]),
                )
            msg_list1.append(msg)

        message1 = xbos_pb2.XBOS(
            drsigpred=dr_signals_pb2.DRSignalsPrediction(
                time=tim,
                predictions=msg_list1
            )
        )

        await self.publish(self.namespace, self.base_resource1, False, message1)

        # # Publish to constraints forecast
        # msg_list2 = []
        # for index, row in df.iterrows():
        #     msg = constraints_forecast_pb2.ConstraintForecast.Constraints(
        #         forecast_time=int(index.tz_localize('US/Pacific').tz_convert('UTC').timestamp()),
        #         PMin=types.Double(value=row['pmin']),
        #         PMax=types.Double(value=row['pmax'])
        #     )
        #     msg_list2.append(msg)

        # message2 = xbos_pb2.XBOS(
        #     constraints_forecast=constraints_forecast_pb2.ConstraintForecast(
        #         time=tim,
        #         constraints_predictions=msg_list2
        #     )
        # )
        # await self.publish(self.namespace, self.base_resource2, False, message2)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('config_file', help='config file')

    args = parser.parse_args()
    config_file = args.config_file

    with open(config_file) as f:
        driverConfig = yaml.safe_load(f)

    logging.basicConfig(level="INFO", format='%(asctime)s - %(name)s - %(message)s')
    dr_signal_driver = DRSignalsDriver(driverConfig)
    # dr_signal_driver.begin()
    run_loop()


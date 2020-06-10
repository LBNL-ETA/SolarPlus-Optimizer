import os
import argparse
import yaml
import logging
import json
import pytz
import datetime
import pandas as pd
from datetime import timedelta
from collections import defaultdict
from dateutil.parser import parse

import electricitycostcalculator
from electricitycostcalculator.cost_calculator.cost_calculator import CostCalculator
from electricitycostcalculator.cost_calculator.tariff_structure import *
from electricitycostcalculator.openei_tariff.openei_tariff_analyzer import *
costcalculator_path = os.path.dirname(electricitycostcalculator.__file__) + '/'

from pyxbos import constraints_forecast_pb2
from pyxbos import dr_signals_pb2
from pyxbos import xbos_pb2
from pyxbos.driver import *
from pyxbos.process import XBOSProcess, b64decode, schedule, run_loop

"""
1. Current assumption includes that no two events have overlapping times.
2. All times in the dr-events.json should be in UTC.
3. All end-dates in the json file are within the 48 hour period.
"""


class DRSignalsDriver(XBOSProcess):

    def __init__(self, cfg):
        """ Constructor.

            Parameters
            ----------
            cfg     : str
                Configuration file.
        """
        super().__init__(cfg)

        self.custom_events = defaultdict(list)
        self.default_events = {}
        
        self.EVENTS_FILE = 'dr_events.json'
        self.forecast_frequency = '15min'

        # CostCalculator instance.
        self.__tariff_manager = CostCalculator()

        # Logging
        self.FORMAT = '%(asctime)-15s %(message)s'
        logging.basicConfig(format=self.FORMAT)
        self.logger = logging.getLogger('DR-SERVER')
        self.logger.setLevel(logging.INFO)

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

    @staticmethod
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

    def read_json_file(self):
        """ Reads the self.EVENTS_FILE json file and stores it in class. """
        if os.path.isfile(self.EVENTS_FILE):
            events = self.read_from_json(self.EVENTS_FILE)
            assert type(events) == list
            
            # CHECK: Add checking to ensure there's no overlapping of event times

            for event in events:
                # CHECK: Error checking - all assert statements go here
                if 'default' in event and event['default']:
                    self.default_events[event['type']] = event
                else:
                    self.custom_events[event['type']].append(event)
        else:
            raise FileNotFoundError(self.EVENTS_FILE + ' file not found')

    def get_utc_start_end_time(self):
        """ Returns current UTC time and curr + forecast_period time

        Returns
        -------
        datetime, datetime
            Current time, currrent time + forecast_period 
        """
        curr_time = datetime.utcnow()
        end_time = curr_time + timedelta(hours=self.FORECAST_PERIOD)
        return curr_time, end_time

    def get_tariff(self, event, curr_time, end_time, default=False):
        """ Gets tariff values from electricitycostcalculator library between two time periods.

        Parameters
        ----------
        event    : dict
            Dictionary containing the tariff file.
        curr_time : datetime
            Current time.
        end_time  : datetime
            Current time + forecast_period.
        default   : bool
            If true, get default tariff.

        Returns
        -------
        pd.DataFrame
            Dataframe containing tariff between the two time periods.
        """
        if default:
            event = self.default_events['price-tou']

        # Init the CostCalculator with the tariff data
        tariff_data = OpenEI_tariff()
        tariff_data.read_from_json(costcalculator_path + event['data']['tariff-json'])

        # Now __tariff_manager has the blocks that defines the tariff
        tariff_struct_from_openei_data(tariff_data, self.__tariff_manager)

        # Get the price signal
        if self.forecast_frequency == '15min':
            timestep = TariffElemPeriod.QUARTERLY
        else:
            raise NotImplementedError('Only 15min frequency works for now.')

        # CHECK if electricitycostcalculator accepts UTC time
        local_curr_time = curr_time.replace(tzinfo=pytz.utc).astimezone(pytz.timezone('US/Pacific'))
        local_end_time = end_time.replace(tzinfo=pytz.utc).astimezone(pytz.timezone('US/Pacific'))

        price_df, map = self.__tariff_manager.get_electricity_price((local_curr_time, local_end_time), timestep)
        price_df['customer_demand_charge_tou'] = price_df['customer_demand_charge_tou'] + price_df['customer_demand_charge_season']
        price_df = price_df.tz_convert('UTC').tz_localize(None)

        return price_df

    def get_rtp(self, event, curr_time, end_time):
        """ Gets real time price values from between two time periods.

        Parameters
        ----------
        event    : dict
            Dictionary containing the real time prices.
        curr_time : datetime
            Current time.
        end_time  : datetime
            Current time + forecast_period.

        Returns
        -------
        pd.DataFrame
            Dataframe containing real time prices between the two time periods.
        """
        # Error checking
        assert len(event['data']['energy_prices']) == len(event['data']['demand_prices'])
        
        delta_sec = (parse(event['end-date']) - parse(event['start-date'])).total_seconds()
        if self.forecast_frequency == '15min':
            step = timedelta(minutes=15)
        else:
            raise NotImplementedError('Only 15min frequency works for now.')
        assert len(event['data']['energy_prices']) == (delta_sec / step.total_seconds())

        array = []
        for index, i in enumerate(range(0, int(delta_sec), int(step.total_seconds()))):
            array.append([curr_time + timedelta(seconds=i),
                            event['data']['energy_prices'][index],
                            event['data']['demand_prices'][index]])
        price_df = pd.DataFrame(array, columns=['timestamp',
                                                'customer_energy_charge',
                                                'customer_demand_charge_tou'])
        price_df.set_index(price_df.columns[0], inplace=True)
        price_df = price_df.tz_localize('US/Pacific').tz_convert('UTC').tz_localize(None)

        return price_df

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
        result = pd.DataFrame()

        if 'price-tou' in self.custom_events:
            price_tou_df = pd.DataFrame()
            price_tou_events = self.custom_events['price-tou']
            
            # Loop through all price-tou events
            for price_tou_event in price_tou_events:
                # Use only those events that are within (curr_time, end_time)
                if datetime.strptime(price_tou_event['start-date'], '%Y-%m-%dT%H:%M:%SZ') >= curr_time:
                    temp = self.get_tariff(price_tou_event, curr_time, end_time)
                    price_tou_df = price_tou_df.append(temp)
            result = pd.concat([result, price_tou_df], sort=True)

        if 'price-rtp' in self.custom_events:
            price_rtp_df = pd.DataFrame()
            price_rtp_events = self.custom_events['price-rtp']

            # Loop through all price-rtp events
            for price_rtp_event in price_rtp_events:
                # Use only those events that are within (curr_time, end_time)
                if datetime.strptime(price_rtp_event['start-date'], '%Y-%m-%dT%H:%M:%SZ') >= curr_time:
                    temp = self.get_rtp(price_rtp_event, curr_time, end_time)
                    price_rtp_df = price_rtp_df.append(temp)
            result = pd.concat([result, price_rtp_df], sort=True)
        
        else:
            raise KeyError('cannot find tariff-json or (energy_prices and demand_prices)')

        # Revert to default tariff
        if result.empty:
            self.logger.info('dr-price default event')
            price_df = self.get_tariff(None, curr_time, end_time, default=True)
            return price_df

        # Custom event
        else:
            self.logger.info('dr-price custom event')

            # custom_st(et) are pandas.Timestamp
            custom_st, custom_et = result.index[0], result.index[-1]
            price_df = result.copy()

            if custom_st > curr_time:
                default_result = self.get_tariff(None, curr_time, custom_st, default=True)
                price_df = pd.concat([default_result, price_df], sort=True)
            if custom_et < end_time:
                default_result = self.get_tariff(None, custom_et, end_time, default=True)
                price_df = pd.concat([price_df, default_result], sort=True)

        return price_df[['customer_energy_charge', 'customer_demand_charge_tou']]

    def get_dr_limit(self, curr_time, end_time):
        """ Gets dr-limit power.

        Parameters
        ----------
        curr_time   : datetime
            Current time.
        end_time    : datetime
            Forecast end time.

        Returns
        -------
        pd.DataFrame
            Dataframe containing dr-limit and dr-mode values
        """
        index = pd.date_range(start=curr_time, end=end_time, freq='15T')
        result = pd.DataFrame(index=index, columns=['pmin', 'pmax', 'dr-mode'])

        dr_limit_events = self.custom_events['dr-limit']
        
        for dr_limit_event in dr_limit_events:
            if datetime.strptime(dr_limit_event['start-date'], '%Y-%m-%dT%H:%M:%SZ') >= curr_time:
                self.logger.info('dr-limit custom event')
                dr_limit = dr_limit_event['data']['power']
                start_date = dr_limit_event['start-date']
                end_date = dr_limit_event['end-date']
                result.loc[start_date:end_date, 'pmax'] = dr_limit
                result.loc[start_date:end_date, 'dr-mode'] = 'dr-limit'

        return result

    def get_dr_shed(self, curr_time, end_time):
        """ Gets dr-shed power.

        Parameters
        ----------
        curr_time   : datetime
            Current time.
        end_time    : datetime
            Forecast end time.

        Returns
        -------
        pd.DataFrame
            Dataframe containing dr-shed and dr-mode values
        """
        index = pd.date_range(start=curr_time, end=end_time, freq='15T')
        result = pd.DataFrame(index=index, columns=['pmin', 'pmax', 'dr-mode'])

        dr_shed_events = self.custom_events['dr-shed']

        for dr_shed_event in dr_shed_events:
            # Checks to see the number of values in "baseline" field is equivalent to the time periods provided
            delta_sec = (parse(dr_shed_event['end-date']) - parse(dr_shed_event['start-date'])).total_seconds()
            step = timedelta(minutes=15)
            assert len(dr_shed_event['data']['baseline']) == (delta_sec / step.total_seconds())

            if datetime.strptime(dr_shed_event['start-date'], '%Y-%m-%dT%H:%M:%SZ') >= curr_time:
                self.logger.info('dr-shed custom event')
                dr_shed = dr_shed_event['data']['power']
                start_date = dr_shed_event['start-date']
                end_date = dr_shed_event['end-date']
                dr_shed_data = [baseline_power + dr_shed for baseline_power in dr_shed_event['data']['baseline']]
                result.loc[start_date:end_date, 'pmax'] = dr_shed_data
                result.loc[start_date:end_date, 'dr-mode'] = 'dr-shed'

        return result

    def get_dr_shift(self, curr_time, end_time):
        """ Gets dr-shift power.

        Parameters
        ----------
        curr_time   : datetime
            Current time.
        end_time    : datetime
            Forecast end time.

        Returns
        -------
        pd.DataFrame
            Dataframe containing dr-shift and dr-mode values
        """
        index = pd.date_range(start=curr_time, end=end_time, freq='15T')
        result = pd.DataFrame(index=index, columns=['pmin', 'pmax', 'dr-mode'])

        dr_shift_events = self.custom_events['dr-shift']

        for dr_shift_event in dr_shift_events:
            # Checks to see the number of values in "baseline" field is equivalent to the time periods provided
            delta_sec_take = (parse(dr_shift_event['end-date-take']) - parse(dr_shift_event['start-date-take'])).total_seconds()
            delta_sec_relax = (parse(dr_shift_event['end-date-relax']) - parse(dr_shift_event['start-date-relax'])).total_seconds()
            step = timedelta(minutes=15)
            assert len(dr_shift_event['data']['baseline-take']) == (delta_sec_take / step.total_seconds())
            assert len(dr_shift_event['data']['baseline-relax']) == (delta_sec_relax / step.total_seconds())

            if datetime.strptime(dr_shift_event['start-date-take'], '%Y-%m-%dT%H:%M:%SZ') >= curr_time:
                self.logger.info('dr-shift custom event')

                # Extract all the values from dict
                dr_shift_take = dr_shift_event['data']['power-take']
                start_date_take = dr_shift_event['start-date-take']
                end_date_take = dr_shift_event['end-date-take']
                dr_shift_relax = dr_shift_event['data']['power-relax']
                start_date_relax = dr_shift_event['start-date-relax']
                end_date_relax = dr_shift_event['end-date-relax']

                dr_shift_take_data = [baseline_power + dr_shift_take for baseline_power in dr_shift_event['data']['baseline-take']]
                dr_shift_relax_data = [baseline_power + dr_shift_relax for baseline_power in dr_shift_event['data']['baseline-relax']]

                result.loc[start_date_take:end_date_take, 'pmin'] = dr_shift_take_data
                result.loc[start_date_take:end_date_take, 'dr-mode'] = 'dr-shift'
                result.loc[start_date_relax:end_date_relax, 'pmax'] = dr_shift_relax_data
                result.loc[start_date_relax:end_date_relax, 'dr-mode'] = 'dr-shift'

        return result

    def get_dr_track(self, curr_time, end_time):
        """ Gets dr-track power.

        Parameters
        ----------
        curr_time   : datetime
            Current time.
        end_time    : datetime
            Forecast end time.

        Returns
        -------
        pd.DataFrame
            Dataframe containing dr-track and dr-mode values
        """
        index = pd.date_range(start=curr_time, end=end_time, freq='15T')
        result = pd.DataFrame(index=index, columns=['pmin', 'pmax', 'dr-mode'])

        dr_track_events = self.custom_events['dr-track']

        for dr_track_event in dr_track_events:
            # Checks to see the number of values in "profile" field is equivalent to the time periods provided
            delta_sec = (parse(dr_track_event['end-date']) - parse(dr_track_event['start-date'])).total_seconds()
            step = timedelta(minutes=15)
            assert len(dr_track_event['data']['profile']) == (delta_sec / step.total_seconds())

            if datetime.strptime(dr_track_event['start-date'], '%Y-%m-%dT%H:%M:%SZ') >= curr_time:
                self.logger.info('dr-track custom event')
                dr_track = dr_track_event['data']['profile']
                start_date = dr_track_event['start-date']
                end_date = dr_track_event['end-date']
                result.loc[start_date:end_date, 'pmax'] = dr_track
                result.loc[start_date:end_date, 'dr-mode'] = 'dr-track'

        return result

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
        pd.DataFrame()
            Dataframe containing power values from all events (limit, shed, shift, track).
        """
        limit = self.get_dr_limit(curr_time, end_time)
        shed = self.get_dr_shed(curr_time, end_time)
        shift = self.get_dr_shift(curr_time, end_time)
        track = self.get_dr_track(curr_time, end_time)

        index = pd.date_range(start=curr_time, end=end_time, freq='15T')
        result = pd.DataFrame(index=index, columns=['pmin', 'pmax', 'dr-mode'])        
        result = result.combine_first(limit).combine_first(shed).combine_first(shift).combine_first(track)

        return result

    async def read(self):
        # Read the events list, see if there are new ones and add them
        self.logger.info("Reading dr_events.json file...")
        self.read_json_file()

        curr_time, end_time = self.get_utc_start_end_time()
        
        df_price = self.get_price(curr_time, end_time)
        df_price.index = df_price.index.round(self.forecast_frequency)

        df_power = self.get_power(curr_time, end_time)
        df_power.index = df_power.index.round(self.forecast_frequency)

        # Combine price and power dataframe and fill in missing values
        df = df_price.join(df_power, how='outer')
        df['pmin'].fillna(self.default_pmin, inplace=True)
        df['pmax'].fillna(self.default_pmax, inplace=True)

        tim = int(time.time() * 1e9)

        msg_list1 = []
        for index, row in df.iterrows():
            # CHECK: Change this to pmin, pmax instead? Keep pmax as the power values
            # all events != dr-shift
            if row['dr-mode'] == 'dr-track':
                msg = dr_signals_pb2.DRSignalsPrediction.Prediction(
                    forecast_time=int(index.timestamp()),
                    price_energy=types.Double(value=row['customer_energy_charge']),
                    price_demand=types.Double(value=row['customer_demand_charge_tou']),
                    signal_type=types.Uint64(value=row['dr-mode']),
                    power_track=types.Double(value=row['pmax'])
                )
            elif not row['dr-mode']:
                msg = dr_signals_pb2.DRSignalsPrediction.Prediction(
                    forecast_time=int(index.timestamp()),
                    price_energy=types.Double(value=row['customer_energy_charge']),
                    price_demand=types.Double(value=row['customer_demand_charge_tou']),
                    signal_type=types.Uint64(value=row['dr-mode'])
                )
            else:
                msg = dr_signals_pb2.DRSignalsPrediction.Prediction(
                    forecast_time=int(index.timestamp()),
                    price_energy=types.Double(value=row['customer_energy_charge']),
                    price_demand=types.Double(value=row['customer_demand_charge_tou']),
                    signal_type=types.Uint64(value=row['dr-mode']),
                    power_limit=types.Double(value=row['pmax'])
                )
            msg_list1.append(msg)

        message1 = xbos_pb2.XBOS(
            drsigpred=dr_signals_pb2.DRSignalsPrediction(
                time=tim,
                predictions=msg_list1
            )
        )
        await self.publish(self.namespace, self.base_resource1, False, message1)

        # Publish to constraints forecast
        msg_list2 = []
        for index, row in df.iterrows():
             msg = constraints_forecast_pb2.ConstraintForecast.Constraints(
                forecast_time=int(index.timestamp()),
                PMin=types.Double(value=row['pmin']),
                PMax=types.Double(value=row['pmax'])
             )
             msg_list2.append(msg)

        message2 = xbos_pb2.XBOS(
            constraints_forecast=constraints_forecast_pb2.ConstraintForecast(
                time=tim,
                constraints_predictions=msg_list2
            )
        )
        await self.publish(self.namespace, self.base_resource2, False, message2)


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('config_file', help='config file')

    args = parser.parse_args()
    config_file = args.config_file

    with open(config_file) as f:
        driverConfig = yaml.safe_load(f)

    dr_signal_driver = DRSignalsDriver(driverConfig)
    dr_signal_driver.read()

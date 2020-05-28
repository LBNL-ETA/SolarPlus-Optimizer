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

"""
1. Current assumption includes that no two events have overlapping times.
2. All times in the dr-events.json should be in UTC.
"""


class DRSignalsDriver():

    def __init__(self, cfg):
        """ Constructor.

            Parameters
            ----------
            cfg     : str
                Configuration file.
        """
        # super().__init__(cfg)

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
        # self.namespace = b64decode(cfg['namespace'])

        # Keeps track of how further into the future should the forecast be
        # Value is in number of hours
        self.FORECAST_PERIOD = cfg['forecast_period']

        # Store the default values for min and max power
        self.default_pmin = cfg['pmin']
        self.default_pmax = cfg['pmax']

        # Publishing rate
        self._rate = cfg['rate']

        # Get DR Signals every _rate seconds and publish
        # schedule(self.call_periodic(self._rate, self.read, runfirst=True))

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

    @staticmethod
    def pretty(d, indent=0):
        for key, value in d.items():
            print('\t' * indent + str(key))
            if isinstance(value, dict):
                pretty(value, indent+1)
            else:
                print('\t' * (indent+1) + str(value))

    def read_json_file(self):
        """ Reads the self.EVENTS_FILE json file. """
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

    def get_dr_signal(self, dr_type, start_time, end_time):
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
        if dr_type == 'dr-prices':
            # 'price-tou', 'price-rtp', 'tariff'
            pass

    def get_utc_start_end_time(self):
        curr_time = datetime.utcnow()
        end_time = curr_time + timedelta(hours=self.FORECAST_PERIOD)
        return curr_time, end_time

    def get_tariff(self, event, curr_time, end_time, default=False):

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

        # CHECK: Double check
        local_curr_time = curr_time.replace(tzinfo=pytz.utc).astimezone(pytz.timezone('US/Pacific'))
        local_end_time = end_time.replace(tzinfo=pytz.utc).astimezone(pytz.timezone('US/Pacific'))

        price_df, map = self.__tariff_manager.get_electricity_price((local_curr_time, local_end_time), timestep)
        price_df['customer_demand_charge_tou'] = price_df['customer_demand_charge_tou'] + price_df['customer_demand_charge_season']
        # price_df = price_df.tz_localize('US/Pacific').tz_convert('UTC').tz_localize(None)
        price_df = price_df.tz_convert('UTC').tz_localize(None)

        return price_df

    def get_rtp(self, event, curr_time, end_time):
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
        curr_time_formatted = curr_time.strftime('%Y-%m-%dT%H:%M:%SZ')
        end_time_formatted = end_time.strftime('%Y-%m-%dT%H:%M:%SZ')

        result = pd.DataFrame()

        if 'price-tou' in self.custom_events:
            price_tou_df = pd.DataFrame()
            price_tou_events = self.custom_events['price-tou']
            for price_tou_event in price_tou_events:
                if datetime.strptime(price_tou_event['start-date'], '%Y-%m-%dT%H:%M:%SZ') >= curr_time:
                    temp = self.get_tariff(price_tou_event, curr_time, end_time)
                    price_tou_df = price_tou_df.append(temp)
            result = pd.concat([result, price_tou_df], sort=True)

        if 'price-rtp' in self.custom_events:
            price_rtp_df = pd.DataFrame()
            price_rtp_events = self.custom_events['price-rtp']
            for price_rtp_event in price_rtp_events:
                if datetime.strptime(price_rtp_event['start-date'], '%Y-%m-%dT%H:%M:%SZ') >= curr_time:
                    temp = self.get_rtp(price_rtp_event, curr_time, end_time)
                    price_rtp_df = price_rtp_df.append(temp)
            result = pd.concat([result, price_rtp_df], sort=True)
        
        else:
            raise KeyError('cannot find tariff-json or (energy_prices and demand_prices)')

        # Revert to default event
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
        
        index = pd.date_range(start=curr_time, end=end_time, freq='15T')
        result = pd.DataFrame(index=index, columns=['pmin', 'pmax', 'dr-mode'])

        dr_limit_events = self.custom_events['dr-limit']
        
        for dr_limit_event in dr_limit_events:
            if datetime.strptime(dr_limit_event['start-date'], '%Y-%m-%dT%H:%M:%SZ') >= curr_time:
                self.logger.info('dr-limit custom event')
                dr_limit = dr_limit_event['data']['power']
                start_date = dr_limit_event['start-date']
                end_date = dr_limit_event['end-date']
                result.loc[start_date  : end_date, 'pmax'] = dr_limit
                result.loc[start_date : end_date, 'dr-mode'] = 'dr-limit'

        return result

    def get_dr_shed(self, curr_time, end_time):

        index = pd.date_range(start=curr_time, end=end_time, freq='15T')
        result = pd.DataFrame(index=index, columns=['pmin', 'pmax'])

        dr_shed_events = self.custom_events['dr-shed']

        for dr_shed_event in dr_shed_events:
            delta_sec = (parse(dr_shed_event['end-date']) - parse(dr_shed_event['start-date'])).total_seconds()
            step = timedelta(minutes=15)
            assert len(dr_shed_event['data']['baseline']) == (delta_sec / step.total_seconds())

            if datetime.strptime(dr_shed_event['start-date'], '%Y-%m-%dT%H:%M:%SZ') >= curr_time:
                self.logger.info('dr-shed custom event')
                dr_shed = dr_shed_event['data']['power']
                start_date = dr_shed_event['start-date']
                end_date = dr_shed_event['end-date']
                dr_shed_data = [baseline_power + dr_shed for baseline_power in dr_shed_event['data']['baseline']]
                # result.loc[start_date : end_date, 'pmax'] = [dr_shed_data for _ in range(result.loc[start_date:end_date].shape[0])]
                result.loc[start_date : end_date, 'pmax'] = dr_shed_data
                result.loc[start_date : end_date, 'dr-mode'] = 'dr-shed'

        return result

    def get_dr_shift(self, curr_time, end_time):
        # CHECK: Modify this for take/relax feature

        index = pd.date_range(start=curr_time, end=end_time, freq='15T')
        result = pd.DataFrame(index=index, columns=['pmin', 'pmax'])

        dr_shift_events = self.custom_events['dr-shift']

        for dr_shift_event in dr_shift_events:
            delta_sec = (parse(dr_shift_event['end-date-relax']) - parse(dr_shift_event['start-date-take'])).total_seconds()
            step = timedelta(minutes=15)
            assert len(dr_shift_event['data']['baseline']) == (delta_sec / step.total_seconds())

            if datetime.strptime(dr_shift_event['start-date-take'], '%Y-%m-%dT%H:%M:%SZ') >= curr_time:
                self.logger.info('dr-shift custom event')
                dr_shift_take = dr_shift_event['data']['power-take']
                start_date_take = dr_shift_event['start-date-take']
                end_date_take = dr_shift_event['end-date-take']
                dr_shift_relax = dr_shift_event['data']['power-relax']
                start_date_relax = dr_shift_event['start-date-relax']
                end_date_relax = dr_shift_event['end-date-relax']

                delta_take_sec = (parse(dr_shift_event['end-date-take']) - parse(dr_shift_event['start-date-take'])).total_seconds()
                delta_relax_sec = (parse(dr_shift_event['end-date-take']) - parse(dr_shift_event['start-date-take'])).total_seconds()

                dr_shift_take_data = [baseline_power + dr_shift_take for baseline_power in dr_shift_event['data']['baseline'][:int(delta_take_sec/step.total_seconds())]]
                dr_shift_relax_data = [baseline_power + dr_shift_relax for baseline_power in dr_shift_event['data']['baseline'][int(delta_take_sec/step.total_seconds()):]]

                result.loc[start_date_take : end_date_take, 'pmin'] = dr_shift_take_data
                result.loc[start_date_take : end_date_take, 'dr-mode'] = 'dr-shift'
                result.loc[start_date_relax : end_date_relax, 'pmax'] = dr_shift_relax_data
                result.loc[start_date_relax : end_date_relax, 'dr-mode'] = 'dr-shift'

        return result

    def get_dr_track(self, curr_time, end_time):

        index = pd.date_range(start=curr_time, end=end_time, freq='15T')
        result = pd.DataFrame(index=index, columns=['pmin', 'pmax'])

        dr_track_events = self.custom_events['dr-track']

        for dr_track_event in dr_track_events:
            delta_sec = (parse(dr_track_event['end-date']) - parse(dr_track_event['start-date'])).total_seconds()
            step = timedelta(minutes=15)
            assert len(dr_track_event['data']['profile']) == (delta_sec / step.total_seconds())

            if datetime.strptime(dr_track_event['start-date'], '%Y-%m-%dT%H:%M:%SZ') >= curr_time:
                self.logger.info('dr-track custom event')
                dr_track = dr_track_event['data']['profile']
                start_date = dr_track_event['start-date']
                end_date = dr_track_event['end-date']
                result.loc[start_date : end_date, 'pmax'] = dr_track
                result.loc[start_date : end_date, 'dr-mode'] = 'dr-track'

        return result

    def get_power(self, curr_time, end_time):
        limit = self.get_dr_limit(curr_time, end_time)
        shed = self.get_dr_shed(curr_time, end_time)
        shift = self.get_dr_shift(curr_time, end_time)
        track = self.get_dr_track(curr_time, end_time)

        result = pd.DataFrame()
        # CHECK: concat is wrong. use join/merge.
        result = pd.concat([limit, shed, shift, track], sort=True)
        # result.to_csv('df.csv')

        return result

    # CHECK: Add "async read(self)" in final version
    def read(self):

        # Read the events list, see if there are new ones and add them
        self.logger.info("Reading dr_events.json file...")

        self.read_json_file()

        curr_time, end_time = self.get_utc_start_end_time()
        
        df_price = self.get_price(curr_time, end_time)
        df_price.index = df_price.index.round(self.forecast_frequency)

        df_power = self.get_power(curr_time, end_time)
        df_power.index = df_power.index.round(self.forecast_frequency)

        # CHECK: This join is giving duplicates. Fix this.
        df = df_price.join(df_power, how='outer')
        df.index = pd.to_datetime(df.index)
        df['pmin'].fillna(self.default_pmin, inplace=True)
        df['pmax'].fillna(self.default_pmax, inplace=True)

        df.to_csv('df.csv')


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('config_file', help='config file')

    args = parser.parse_args()
    config_file = args.config_file

    with open(config_file) as f:
        driverConfig = yaml.safe_load(f)

    dr_signal_driver = DRSignalsDriver(driverConfig)
    dr_signal_driver.read()

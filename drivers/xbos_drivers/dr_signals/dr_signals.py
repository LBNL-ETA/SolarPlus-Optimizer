import time
import argparse
import yaml
import logging
import json
import pytz
import pandas as pd
import datetime
import numpy as np

from electricitycostcalculator.cost_calculator.cost_calculator import CostCalculator
from electricitycostcalculator.openei_tariff.openei_tariff_analyzer import OpenEI_tariff, tariff_struct_from_openei_data, TariffElemPeriod

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
        self.dr_events_file = cfg.get('dr_events_file', 'dr_events.json')

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
        self.FORECAST_PERIOD = cfg.get('forecast_period', 48)
        self.forecast_frequency = cfg.get('forecast_frequency', 15)

        # Store the default values for min and max power
        self.default_pmin = cfg.get('default_pmin', -999999)
        self.default_pmax = cfg.get('default_pmax', 999999)

        # Publishing rate
        self._rate = cfg['rate']

        self.tz_local = pytz.timezone("America/Los_Angeles")
        self.tz_utc = pytz.timezone("UTC")

        # Get DR Signals every _rate seconds and publish
        schedule(self.call_periodic(self._rate, self.read, runfirst=True))

    def parse_event_datetime(self, dt):
        # still in local time
        return datetime.datetime.strptime(dt, "%Y-%m-%dT%H:%M:%SZ")

    def get_tou(self, event):
        """ Gets tariff values from electricitycostcalculator library between two time periods.

        """
        if self.forecast_frequency == 15:
            timestep = TariffElemPeriod.QUARTERLY
        else:
            raise NotImplementedError('Only 15min frequency works for now.')

        event_st_local = self.parse_event_datetime(event['start-date'])
        event_et_local = self.parse_event_datetime(event['end-date'])

        tariff_data = OpenEI_tariff()
        tariff_data.read_from_json(event['data']['tariff-json'])

        cost_calculator = CostCalculator()
        tariff_struct_from_openei_data(tariff_data, cost_calculator)

        p_df, price_map = cost_calculator.get_electricity_price((event_st_local, event_et_local), timestep)
        p_df = p_df.fillna(0)

        price_df = p_df[['customer_energy_charge']]
        price_df.columns = ['pi_e']
        price_df['pi_d'] = p_df.customer_demand_charge_season + p_df.customer_demand_charge_tou
        price_df = price_df.tz_localize(self.tz_local).tz_convert(self.tz_utc).tz_localize(None)

        return price_df

    def get_rtp(self, event):
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

        event_st_local = self.parse_event_datetime(event['start-date'])
        event_et_local = self.parse_event_datetime(event['end-date'])
        delta_sec = (event_et_local - event_st_local).total_seconds()

        if self.forecast_frequency == 15:
            step = '15T'
        else:
            raise NotImplementedError('Only 15min frequency works for now.')
        assert len(event['data']['energy_prices']) == (delta_sec / (self.forecast_frequency * 60))

        price_df = pd.DataFrame(index=pd.date_range(event_st_local, event_et_local, freq=step, closed='left'),
                                data={'pi_e': event['data']['energy_prices'], 'pi_d': event['data']['demand_prices']})
        price_df = price_df.tz_localize(self.tz_local).tz_convert(self.tz_utc).tz_localize(None)
        return price_df

    def get_dr_limit(self, event):
        """ Gets dr-limit power.

        """
        event_st_local = self.parse_event_datetime(event['start-date'])
        event_et_local = self.parse_event_datetime(event['end-date'])
        if self.forecast_frequency == 15:
            step = '15T'
        else:
            raise NotImplementedError('Only 15min frequency works for now.')
        idx = pd.date_range(event_st_local, event_et_local, freq=step, closed='left')
        num_elem = idx.shape[0]

        power_df = pd.DataFrame(index=idx, data={'pmax': num_elem * [event['data']['power']]})
        power_df = power_df.tz_localize(self.tz_local).tz_convert(self.tz_utc).tz_localize(None)
        return power_df

    def get_dr_shed(self, event):
        """ Gets dr-shed power.

        """
        event_st_local = self.parse_event_datetime(event['start-date'])
        event_et_local = self.parse_event_datetime(event['end-date'])
        if self.forecast_frequency == 15:
            step = '15T'
        else:
            raise NotImplementedError('Only 15min frequency works for now.')
        idx = pd.date_range(event_st_local, event_et_local, freq=step, closed='left')
        num_elem = idx.shape[0]

        shed_power = np.array(num_elem * [event['data']['power']])
        baseline_power = np.array(event['data']['baseline'])
        assert len(baseline_power) == num_elem
        pmax = baseline_power + shed_power

        power_df = pd.DataFrame(index=idx, data={'pmax': pmax})
        power_df = power_df.tz_localize(self.tz_local).tz_convert(self.tz_utc).tz_localize(None)
        return power_df

    def get_dr_shift(self, event):
        """ Gets dr-shift power.

        """
        event_st_take_local = self.parse_event_datetime(event['start-date-take'])
        event_et_take_local = self.parse_event_datetime(event['end-date-take'])
        event_st_relax_local = self.parse_event_datetime(event['start-date-relax'])
        event_et_relax_local = self.parse_event_datetime(event['end-date-relax'])

        if self.forecast_frequency == 15:
            step = '15T'
        else:
            raise NotImplementedError('Only 15min frequency works for now.')

        # Take == increase power consumption
        idx1 = pd.date_range(event_st_take_local, event_et_take_local, freq=step, closed='left')
        num_elem1 = idx1.shape[0]
        take_power = np.array(num_elem1 * [event['data']['power-take']])
        baseline_take_power = np.array(event['data']['baseline-take'])
        assert len(baseline_take_power) == num_elem1
        pmin = take_power + baseline_take_power
        power_df1 = pd.DataFrame(index=idx1, data={'pmin': pmin})
        power_df1 = power_df1.tz_localize(self.tz_local).tz_convert(self.tz_utc).tz_localize(None)

        # Relax == decrease power consumption
        idx2 = pd.date_range(event_st_relax_local, event_et_relax_local, freq=step, closed='left')
        num_elem2 = idx2.shape[0]
        relax_power = np.array(num_elem2 * [event['data']['power-relax']])
        baseline_relax_power = np.array(event['data']['baseline-relax'])
        assert len(baseline_relax_power) == num_elem2
        pmax = relax_power + baseline_relax_power
        power_df2 = pd.DataFrame(index=idx2, data={'pmax': pmax})
        power_df2 = power_df2.tz_localize(self.tz_local).tz_convert(self.tz_utc).tz_localize(None)
        return power_df1, power_df2

    def get_dr_track(self, event):
        """ Gets dr-track power.

        """
        event_st_local = self.parse_event_datetime(event['start-date'])
        event_et_local = self.parse_event_datetime(event['end-date'])
        if self.forecast_frequency == 15:
            step = '15T'
        else:
            raise NotImplementedError('Only 15min frequency works for now.')
        idx = pd.date_range(event_st_local, event_et_local, freq=step, closed='left')
        num_elem = idx.shape[0]

        tolerance = np.array(num_elem * [event['data']['tolerance']])
        profile_power = np.array(event['data']['profile'])
        assert len(profile_power) == num_elem
        pmax = profile_power + tolerance
        pmin = profile_power - tolerance

        power_df = pd.DataFrame(index=idx, data={'pmax': pmax, 'pmin': pmin, 'profile': profile_power})
        power_df = power_df.tz_localize(self.tz_local).tz_convert(self.tz_utc).tz_localize(None)

        return power_df

    def get_current_events(self, start_time_utc, end_time_utc):
        with open(self.dr_events_file) as fp:
            events = json.load(fp)

        current_events = []
        for event in events:
            event_type = event['type']
            if event_type == 'dr-shift':
                st1 = datetime.datetime.strptime(event.get('start-date-take'), "%Y-%m-%dT%H:%M:%SZ")
                st2 = datetime.datetime.strptime(event.get('start-date-relax'), "%Y-%m-%dT%H:%M:%SZ")

                et1 = datetime.datetime.strptime(event.get('end-date-take'), "%Y-%m-%dT%H:%M:%SZ")
                et2 = datetime.datetime.strptime(event.get('end-date-relax'), "%Y-%m-%dT%H:%M:%SZ")
                if st1 < st2:
                    st = st1
                else:
                    st = st2

                if et1 > et2:
                    et = et1
                else:
                    et = et2
            else:
                st = datetime.datetime.strptime(event.get('start-date'), "%Y-%m-%dT%H:%M:%SZ")
                et = datetime.datetime.strptime(event.get('end-date'), "%Y-%m-%dT%H:%M:%SZ")
            st = self.tz_local.localize(st)
            et = self.tz_local.localize(et)
            st = st.astimezone(self.tz_utc).replace(tzinfo=None)
            et = et.astimezone(self.tz_utc).replace(tzinfo=None)

            if (start_time_utc > et) or (end_time_utc < st):
                continue
            else:
                current_events.append(event)
        return current_events

    def get_default_df(self, start_time_utc, end_time_utc):
        start_time_local = self.tz_utc.localize(start_time_utc).astimezone(self.tz_local).replace(tzinfo=None)
        end_time_local = self.tz_utc.localize(end_time_utc).astimezone(self.tz_local).replace(tzinfo=None)

        tariff_data = OpenEI_tariff(utility_id='rcea',
                                    sector='Commercial',
                                    tariff_rate_of_interest='E-19S',
                                    distrib_level_of_interest='Secondary',
                                    phasewing=None,
                                    tou=True)
        tariff_data.read_from_json()
        cost_calculator = CostCalculator()
        tariff_struct_from_openei_data(tariff_data, cost_calculator)
        timestep = TariffElemPeriod.QUARTERLY
        p_df, price_map = cost_calculator.get_electricity_price((start_time_local, end_time_local), timestep)
        p_df = p_df.fillna(0)
        price = p_df[['customer_energy_charge']]
        price.columns = ['pi_e']
        price['pi_d'] = p_df.customer_demand_charge_season + p_df.customer_demand_charge_tou
        price = price.tz_localize(self.tz_local).tz_convert(self.tz_utc).tz_localize(None)
        df = price.copy()
        df['pi_e'] = price['pi_e']
        df['pi_d'] = price['pi_d']
        df['pmax'] = self.default_pmax
        df['pmin'] = self.default_pmin
        df['dr-mode'] = 0
        return df

    async def read(self):
        time_now = datetime.datetime.utcnow()
        curr_time_utc = datetime.datetime.combine(time_now.date(), datetime.time(time_now.hour, 0, 0))
        end_time_utc = curr_time_utc + datetime.timedelta(hours=self.FORECAST_PERIOD)
        df = self.get_default_df(start_time_utc=curr_time_utc, end_time_utc=end_time_utc)
        current_events = self.get_current_events(start_time_utc=curr_time_utc, end_time_utc=end_time_utc)

        for event in current_events:
            event_type = event['type']
            print(event_type)

            if event_type == 'price-rtp':
                price_df = self.get_rtp(event=event)
                idx = df.merge(price_df, left_index=True, right_index=True, how='inner').index
                df.loc[idx, 'pi_e'] = price_df.loc[idx, 'pi_e']
                df.loc[idx, 'pi_d'] = price_df.loc[idx, 'pi_d']
                df.loc[idx, 'dr-mode'] = 5
            elif event_type == 'price-tou':
                price_df = self.get_tou(event=event)
                idx = df.merge(price_df, left_index=True, right_index=True, how='inner').index
                df.loc[idx, 'pi_e'] = price_df.loc[idx, 'pi_e']
                df.loc[idx, 'pi_d'] = price_df.loc[idx, 'pi_d']
                df.loc[idx, 'dr-mode'] = 6
            elif event_type == 'dr-limit':
                power_df = self.get_dr_limit(event=event)
                idx = df.merge(power_df, left_index=True, right_index=True, how='inner').index
                df.loc[idx, 'pmax'] = power_df.loc[idx, 'pmax']
                df.loc[idx, 'dr-mode'] = 1
            elif event_type == 'dr-shed':
                power_df = self.get_dr_shed(event=event)
                idx = df.merge(power_df, left_index=True, right_index=True, how='inner').index
                df.loc[idx, 'pmax'] = power_df.loc[idx, 'pmax']
                df.loc[idx, 'dr-mode'] = 2
            elif event_type == 'dr-shift':
                take_df, relax_df = self.get_dr_shift(event=event)
                idx1 = df.merge(take_df, left_index=True, right_index=True, how='inner').index
                df.loc[idx1, 'pmin'] = take_df.loc[idx1, 'pmin']
                df.loc[idx1, 'dr-mode'] = 3
                idx2 = df.merge(relax_df, left_index=True, right_index=True, how='inner').index
                df.loc[idx2, 'pmax'] = relax_df.loc[idx2, 'pmax']
                df.loc[idx2, 'dr-mode'] = 3
            elif event_type == 'dr-track':
                power_df = self.get_dr_track(event=event)
                idx = df.merge(power_df, left_index=True, right_index=True, how='inner').index
                df.loc[idx, 'pmax'] = power_df.loc[idx, 'pmax']
                df.loc[idx, 'pmin'] = power_df.loc[idx, 'pmin']
                df.loc[idx, 'dr-mode'] = 4
                df.loc[idx, 'profile'] = power_df.loc[idx, 'profile']
        tim = int(time.time() * 1e9)

        msg_list1 = []
        for index, row in df.iterrows():
            forecast_time = int(index.value)

            if row['dr-mode'] > 0  and row['dr-mode'] < 5:
                    if row['dr-mode'] == 4:
                        msg = dr_signals_pb2.DRSignalsPrediction.Prediction(
                            forecast_time=int(forecast_time/1e9),
                            price_energy=types.Double(value=row['pi_e']),
                            price_demand=types.Double(value=row['pi_d']),
                            signal_type=types.Uint64(value=int(row['dr-mode'])),
                            power_track=types.Double(value=row['profile'])
                        )
                    else:
                        msg = dr_signals_pb2.DRSignalsPrediction.Prediction(
                            forecast_time=int(forecast_time/1e9),
                            price_energy=types.Double(value=row['pi_e']),
                            price_demand=types.Double(value=row['pi_d']),
                            signal_type=types.Uint64(value=int(row['dr-mode'])),
                            power_limit=types.Double(value=row['pmax'])
                        )
            else:
                msg = dr_signals_pb2.DRSignalsPrediction.Prediction(
                    forecast_time=int(forecast_time/1e9),
                    price_energy=types.Double(value=row['pi_e']),
                    price_demand=types.Double(value=row['pi_d']),
                    signal_type=types.Uint64(value=int(row['dr-mode'])),
                )
            msg_list1.append(msg)

        message1 = xbos_pb2.XBOS(
            drsigpred=dr_signals_pb2.DRSignalsPrediction(
                time=tim,
                predictions=msg_list1
            )
        )
        await self.publish(self.namespace, self.base_resource1, False, message1)
        print("publishing at time={0} to topic={1}".format(
            datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), self.base_resource1))

        # Publish to constraints forecast
        msg_list2 = []
        for index, row in df.iterrows():
             forecast_time = int(index.value)
             msg = constraints_forecast_pb2.ConstraintForecast.Constraints(
                forecast_time=forecast_time,
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
        print("publishing at time={0} to topic={1}".format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                                           self.base_resource2))


parser = argparse.ArgumentParser()
parser.add_argument('config_file', help='config file')

args = parser.parse_args()
config_file = args.config_file

with open(config_file) as f:
    driverConfig = yaml.safe_load(f)

dr_signal_driver = DRSignalsDriver(driverConfig)
run_loop()
import argparse
import datetime
import logging

import pandas as pd
import yaml
from clean_data import Clean_Data
from influxdb import DataFrameClient
from process_data import Process_Data
from pyxbos.process import XBOSProcess, b64decode, schedule, run_loop
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import KFold


# Make below parameter configurable,
# Publish hourly for each baseline method
# Make forecast for two days ahead


class BaselineDriver(XBOSProcess):

    def __init__(self, cfg):
        super().__init__(cfg)

        # Logging
        self.FORMAT = '%(asctime)-15s %(message)s'
        logging.basicConfig(format=self.FORMAT)
        self.logger = logging.getLogger('Baseline-Server')
        self.logger.setLevel(logging.INFO)

        self.base_resource = cfg['xbos']['base_resource']
        self.namespace = b64decode(cfg['xbos']['namespace'])

        # Publishing rate
        self._rate = cfg['xbos']['rate']

        # Get forecast horizon
        self.forecast_horizon = cfg['baseline']['forecast_horizon']

        # Initialize connection to influxdb
        self.influx_cfg = cfg['influx']
        self.init_influx(self.influx_cfg)

        # Get baseline data  every _rate seconds and publish
        schedule(self.call_periodic(self._rate, self.read, runfirst=True))

    @staticmethod
    def adj_r2(r2, n, k):
        """ Calculate and return adjusted r2 score.
        Parameters
        ----------
        r2  :
            Original r2 score.
        n   :
            Number of points in data sample.
        k   :
            Number of variables in model, excluding the constant.
        Returns
        -------
        float
            Adjusted R2 score.
        """
        return 1 - (((1 - r2) * (n - 1)) / (n - k - 1))

    def init_influx(self, influx_cfg):
        self.influx_client = DataFrameClient(host=influx_cfg["host"],
                                             port=influx_cfg["port"],
                                             username=influx_cfg["username"],
                                             password=influx_cfg["password"],
                                             ssl=influx_cfg["ssl"],
                                             verify_ssl=influx_cfg["verify_ssl"],
                                             database=influx_cfg["database"])

    def get_data_from_influx(self, st, measurement, uuid, window, col):
        q = "select value from %s where \"uuid\"=\'%s\'" % (measurement, uuid)
        q += " and time > now() - " + str(st)
        q += " group by time(%s)" % window

        # q = "select %s(value) as value from %s where \"uuid\"=\'%s\'" % (agg, measurement, uuid)
        # q += " and time >= '%s' and time <= '%s'" % (st, et)
        # Below query is more efficienct than the prev one
        # res = self.influx_client.query(
        #    "select last(value), time from timeseries where \"uuid\"=\'%s\' and time > now() - 17m" % uuid)

        df = self.influx_client.query(q)[measurement]
        df.columns = [col]
        return df

    def get_future_data_from_influx(self, horizon, measurement, uuid, window, col):
        st = datetime.datetime.utcnow()
        et = st + datetime.timedelta(days=self.forecast_horizon)
        start_date = st.strftime('%Y-%m-%dT%H:%M:%SZ')
        end_date = et.strftime('%Y-%m-%dT%H:%M:%SZ')

        q = "select value from %s where \"uuid\"=\'%s\'" % (measurement, uuid)
        # q += " and time >= '%s' and time <= '%s'" % (start_date, end_date)
        q += " and time >= '%s'" % (st - datetime.timedelta(hours=1)).strftime('%Y-%m-%dT%H:%M:%SZ')
        q += " order by time desc"
        q += " limit 100"

        df = self.influx_client.query(q)[measurement]
        df.columns = [col]
        return df.loc[df.groupby(df.index).count().idxmax()]

    def regression(self, baseline, predict_col, cv=5):
        baseline_in = baseline[[predict_col]]
        baseline_out = baseline[baseline.columns.difference([predict_col])]

        model = LinearRegression()
        scores = []
        metrics = {}

        kfold = KFold(n_splits=cv, shuffle=True, random_state=42)
        for i, (train, test) in enumerate(kfold.split(baseline_in, baseline_out)):
            model.fit(baseline_in.iloc[train], baseline_out.iloc[train])
            scores.append(model.score(baseline_in.iloc[test], baseline_out.iloc[test]))

        mean_score = sum(scores) / len(scores)

        metrics['Linear Regression'] = {}
        metrics['Linear Regression']['Model'] = model
        metrics['Linear Regression']['R2'] = mean_score
        metrics['Linear Regression']['Adj R2'] = self.adj_r2(mean_score, baseline_in.shape[0], baseline_in.shape[1])

        return metrics

    def clean_process_data(self, power, weather, forecast_weather):
        # TODO: Add event_days parameter and remove all from df

        # Prepare training data
        df = weather.join(power, how='outer')
        df.index = pd.to_datetime(df.index)

        clean_data_obj = Clean_Data(df)
        cleaned_df = clean_data_obj.resample_data(df, '15T')
        cleaned_df1 = clean_data_obj.remove_na(data=cleaned_df, remove_na_how='any')
        cleaned_df2 = clean_data_obj.remove_outlier(data=cleaned_df1, sd_val=4)

        process_data_obj = Process_Data(cleaned_df2)
        processed_data1 = process_data_obj.add_time_features(tod=True)

        # Prepare testing data
        forecast_weather.index = pd.to_datetime(forecast_weather.index)

        timestamp = forecast_weather.index[0].round('15min')
        range_timestamps = [timestamp + datetime.timedelta(hours=x) for x in range(0, len(forecast_weather.values))]

        forecast_weather1 = pd.DataFrame({'time': range_timestamps, 'values': forecast_weather.values.flatten()})
        forecast_weather1.set_index('time', inplace=True)
        forecast_weather1.index = pd.to_datetime(forecast_weather1.index)

        clean_test_data_obj = Clean_Data(forecast_weather1)
        cleaned_test_df = clean_test_data_obj.resample_data(forecast_weather1, '15T')
        cleaned_test_df1 = clean_test_data_obj.interpolate_data(data=cleaned_test_df, limit=None, method='linear')
        cleaned_test_df2 = clean_test_data_obj.remove_na(data=cleaned_test_df1, remove_na_how='any')
        cleaned_test_df3 = clean_test_data_obj.remove_outlier(data=cleaned_test_df2, sd_val=4)

        process_test_data_obj = Process_Data(cleaned_test_df3)
        processed_test_df = process_test_data_obj.add_time_features(tod=True)

        return processed_data1, processed_test_df

    def calculate_baseline(self, power, weather, event_days, forecast_weather, predict_col):
        data, test_data = self.clean_process_data(power, weather, forecast_weather)

        # print('data: \n', data.head(), data.shape)
        # print('test_data: \n', test_data.head(), test_data.shape)

        reg_metrics = self.regression(data, predict_col=predict_col)
        data_model_metrics = DataModel(data, event_day, 10, 10)
        # ten_ten_metrics = ten_of_ten(baseline)

        # TODO: Check which is the best performing model here

        best_model = reg_metrics['Linear Regression']['Model']
        best_model.fit(data[data.columns.difference([predict_col])], data[[predict_col]])

        # TODO: Create test dataframe of weather data

        result = best_model.predict(test_data)

        return result

    async def read(self):
        # st = datetime.datetime.utcnow()
        # et = st + datetime.timedelta(days=self.forecast_horizon)
        # start_date = st.strftime('%Y-%m-%dT%H:%M:%SZ')
        # end_date = et.strftime('%Y-%m-%dT%H:%M:%SZ')
        # agg = 'MEAN'

        historical_data = '90d'
        window = '1min'
        measurement = 'timeseries'

        power_uuid = 'd2004400-349c-5015-8f20-e249953295a7'
        weather_uuid = 'f7c1f2c8-c996-528c-ab3d-bdc96dc9cf72'
        forecast_weather_uuid = '69be4db0-48f5-592f-b5a1-e2e695f28ad1'
        # dr_signals_uuid = 'a89cfc61-9391-5e3e-b89c-5aa969651eb5'

        power_col = 'power (W)'
        weather_col = 'temp (F)'
        forecast_weather_col = 'forecast temp (F)'

        df_power = self.get_data_from_influx(historical_data, measurement, power_uuid, window, power_col)
        df_weather = self.get_data_from_influx(historical_data, measurement, weather_uuid, window, weather_col)
        # df_dr_signals = self.get_data_from_influx(historical_data, measurement, dr_signals_uuid, window)
        df_forecast_weather = self.get_future_data_from_influx(str(self.forecast_horizon) + 'd', measurement,
                                                               forecast_weather_uuid, window, forecast_weather_col)

        result = self.calculate_baseline(df_power, df_weather, None, df_forecast_weather, predict_col=power_col)

        # publish msg to topic /baseline/
        # msg - timestamp, prediction_timestamp, baseline_value, baseline_type


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('config_file', help='config file')

    args = parser.parse_args()
    config_file = args.config_file

    with open(config_file) as f:
        driverConfig = yaml.safe_load(f)

    logging.basicConfig(level="INFO", format='%(asctime)s - %(name)s - %(message)s')
    baseline_driver = BaselineDriver(driverConfig)
    run_loop()

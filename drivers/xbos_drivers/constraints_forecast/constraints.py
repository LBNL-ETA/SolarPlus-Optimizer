import argparse
import datetime
import logging
import time
from datetime import timedelta

import pandas as pd
import yaml
from pyxbos import constraints_forecast_pb2
from pyxbos import xbos_pb2
from pyxbos.driver import *
from pyxbos.process import XBOSProcess, b64decode, schedule, run_loop


class ConstraintsForecastDriver(XBOSProcess):

    def __init__(self, cfg):

        # Logging
        self.FORMAT = '%(asctime)-15s %(message)s'
        logging.basicConfig(format=self.FORMAT)
        self.logger = logging.getLogger('Constraints')
        self.logger.setLevel(logging.INFO)

        self.base_resource = cfg['base_resource']
        self.namespace = b64decode(cfg['namespace'])

        # Publishing rate
        self._rate = cfg['rate']

        # Get constraints file
        self.filename = cfg['csv_file']

        # Get forecast period (units=hours)
        self.FORECAST_PERIOD = cfg['forecast_period']

        # Get constraints every _rate seconds and publish
        schedule(self.call_periodic(self._rate, self.read, runfirst=True))

    async def read(self):

        self.logger.info("Reading constraints file...")

        df_constraints = pd.read_csv(self.filename, index_col=[0], parse_dates=True)

        curr_time = datetime.datetime.today().replace(microsecond=0).replace(second=0)
        end_time = curr_time + timedelta(hours=self.FORECAST_PERIOD)

        index = pd.date_range(curr_time, end_time, freq='min')
        df_temp = pd.DataFrame(index=index)
        df_temp = df_temp.fillna(0)

        df = df_temp.join(df_constraints)
        df = df.ffill().bfill()

        msg_list = []
        for index, row in df.iterrows():
            msg = constraints_forecast_pb2.ConstraintsForecast.Constraints(
                forecast_time=int(index.timestamp()),
                TRtuMin=types.Double(value=row['Trtu_min']),
                TRtuMax=types.Double(value=row['Trtu_max']),
                TRefMax=types.Double(value=row['Tref_max']),
                TRefMin=types.Double(value=row['Tref_min']),
                TFreMax=types.Double(value=row['Tfre_max']),
                TFreMin=types.Double(value=row['Tfre_min']),
                SOCMax=types.Double(value=row['SOC_max']),
                SOCMin=types.Double(value=row['SOC_min']),
                uCoolMin=types.Double(value=row['uCool_min']),
                uCoolMax=types.Double(value=row['uCool_max']),
                uHeatMin=types.Double(value=row['uHeat_min']),
                uHeatMax=types.Double(value=row['uHeat_max']),
                #uChargeMin=types.Double(value=-1),
                #uChargeMax=types.Double(value=-1),
                #uDischargeMin=types.Double(value=-1),
                #uDischargeMax=types.Double(value=-1),
                uRefMin=types.Double(value=row['uRef_min']),
                uRefMax=types.Double(value=row['uRef_max']),
                uFreCoolMin=types.Double(value=row['uFreCool_min']),
                uFreCoolMax=types.Double(value=row['uFreCool_max']),
                #demand=types.Double(value=-1),
                uBatteryMin=types.Double(value=row['uBattery_min']),
                uBatteryMax=types.Double(value=row['uBattery_max']),
                # PMin=types.Double(value=self.constraints_forecast['Pmin']),
                # PMax=types.Double(value=self.constraints_forecast['Pmax'])
            )
            msg_list.append(msg)

        message = xbos_pb2.XBOS(
            constraints_forecast=constraints_forecast_pb2.ConstraintsForecast(
                time=int(time.time() * 1e9),
                constraints_predictions=msg_list
            )
        )

        await self.publish(self.namespace, self.base_resource, False, message)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('config_file', help='config file with csv file and namespace')

    args = parser.parse_args()
    config_file = args.config_file

    with open(config_file) as f:
        driverConfig = yaml.safe_load(f)

    logging.basicConfig(level="INFO", format='%(asctime)s - %(name)s - %(message)s')
    constraints_forecast_driver = ConstraintsForecastDriver(driverConfig)
    run_loop()

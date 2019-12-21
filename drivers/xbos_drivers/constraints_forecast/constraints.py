import argparse
import datetime
import logging
import time
from datetime import timedelta

import yaml
from pyxbos import constraints_forecast_pb2
from pyxbos import xbos_pb2
from pyxbos.driver import *
from pyxbos.process import XBOSProcess, b64decode, schedule, run_loop


class ConstraintsForecastDriver(XBOSProcess):

    def __init__(self, cfg):
        """ Initalize all the constraints from the config file.

        Parameters
        ----------
        cfg     : str
            Relative path to the config file.
        """
        super().__init__(cfg)

        # Logging
        self.FORMAT = '%(asctime)-15s %(message)s'
        logging.basicConfig(format=self.FORMAT)
        self.logger = logging.getLogger('Constraints')
        self.logger.setLevel(logging.INFO)

        self.base_resource = cfg['base_resource']
        self.namespace = b64decode(cfg['namespace'])

        # Publishing rate
        self._rate = cfg['rate']

        # Get forecast period (units=hours)
        self.FORECAST_PERIOD = cfg['forecast_period']

        # Get all constraints
        self.Trtu_max = cfg['Trtu_max']
        self.Trtu_min = cfg['Trtu_min']
        self.Tref_max = cfg['Tref_max']
        self.Tref_min = cfg['Tref_min']
        self.Tfre_max = cfg['Tfre_max']
        self.Tfre_min = cfg['Tfre_min']
        self.SOC_max = cfg['SOC_max']
        self.SOC_min = cfg['SOC_min']
        self.uCool_max = cfg['uCool_max']
        self.uCool_min = cfg['uCool_min']
        self.uHeat_max = cfg['uHeat_max']
        self.uHeat_min = cfg['uHeat_min']
        self.uChargeMax = cfg['uChargeMax']
        self.uChargeMin = cfg['uChargeMin']
        self.uDischargeMax = cfg['uDischargeMax']
        self.uDischargeMin = cfg['uDischargeMin']
        self.uRef_max = cfg['uRef_max']
        self.uRef_min = cfg['uRef_min']
        self.uFreCool_max = cfg['uFreCool_max']
        self.uFreCool_min = cfg['uFreCool_min']
        self.demand = cfg['demand']
        self.uBattery_max = cfg['uBattery_max']
        self.uBattery_min = cfg['uBattery_min']
        self.Pmax = cfg['Pmax']
        self.Pmin = cfg['Pmin']

        # Get constraints every _rate seconds and publish
        schedule(self.call_periodic(self._rate, self.read, runfirst=True))

    async def read(self):
        """ Publish constraints to the namespace specificed in the config file.
        NOTE: PMin and PMax are calculated and published from dr_signals_driver.
        """
        self.logger.info('Publishing constraints...')

        curr_time = datetime.datetime.today().replace(microsecond=0).replace(second=0)
        end_time = curr_time + timedelta(hours=self.FORECAST_PERIOD)
        diff = (end_time - curr_time).total_seconds() / 60

        msg_list = []
        for date in (curr_time + timedelta(minutes=n) for n in range(0, int(diff), 15)):
            msg = constraints_forecast_pb2.ConstraintsForecast.Constraints(
                forecast_time=int(date.timestamp()),
                TRtuMax=types.Double(value=self.Trtu_max),
                TRtuMin=types.Double(value=self.Trtu_min),
                TRefMax=types.Double(value=self.Tref_max),
                TRefMin=types.Double(value=self.Tref_min),
                TFreMax=types.Double(value=self.Tfre_max),
                TFreMin=types.Double(value=self.Tfre_min),
                SOCMax=types.Double(value=self.SOC_max),
                SOCMin=types.Double(value=self.SOC_min),
                uCoolMax=types.Double(value=self.uCool_max),
                uCoolMin=types.Double(value=self.uCool_min),
                uHeatMax=types.Double(value=self.uHeat_max),
                uHeatMin=types.Double(value=self.uHeat_min),
                uChargeMax=types.Double(value=self.uChargeMax),
                uChargeMin=types.Double(value=self.uChargeMin),
                uDischargeMax=types.Double(value=self.uDischargeMax),
                uDischargeMin=types.Double(value=self.uDischargeMin),
                uRefMax=types.Double(value=self.uRef_max),
                uRefMin=types.Double(value=self.uRef_min),
                uFreCoolMax=types.Double(value=self.uFreCool_max),
                uFreCoolMin=types.Double(value=self.uFreCool_min),
                demand=types.Double(value=self.demand),
                uBatteryMax=types.Double(value=self.uBattery_max),
                uBatteryMin=types.Double(value=self.uBattery_min)
                # PMax=types.Double(value=self.PMax),
                # PMin=types.Double(value=self.PMin)
            )
            msg_list.append(msg)

        message = xbos_pb2.XBOS(
            constraints_forecast=constraints_forecast_pb2.ConstraintsForecast(
                time=int(time.time() * 1e9),
                constraints_predictions=msg_list
            )
        )

        #await self.publish(self.namespace, self.base_resource, False, message)


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

import datetime
import pandas as pd
import time
from data_manager import Data_Manager
import baseline_config
import pytz

class Baseline_Controller:
    def __init__(self, config):
        self.config = config
        self.data_manager_config = self.config.get('data_manager_config')
        self.data_manager = Data_Manager(data_manager_config=self.data_manager_config)

        self.max_battery_rate = self.config.get('max_battery_rate', 21000)
        self.min_battery_rate = self.config.get('min_battery_rate', -21000)
        self.max_battery_soc = self.config.get('max_battery_soc', 0.95)
        self.min_battery_soc = self.config.get('min_battery_soc', 0.25)
        self.battery_total_capacity = self.config.get('battery_total_capacity', 40500)

        self.historical_data_interval = self.config.get('historical_data_interval_minutes', 15)
        
        print("The baseline controller has been instantiated")

    def generate_setpoints(self):
        end_time = datetime.datetime.utcnow()
        start_time = end_time - datetime.timedelta(minutes=self.historical_data_interval)

        input_df = self.data_manager.get_timeseries_from_config(config='baseline', start_time=start_time, end_time=end_time)
        average_values = input_df.mean()

        solar_production = average_values.pv_generation
        building_load = average_values.building_load
        battery_soc = average_values.battery_soc

        net_load = building_load - solar_production

        print("\n****************Running baseline controller:")
        print("current solar_production = {0}".format(solar_production))
        print("current building_load = {0}".format(building_load))
        print("current battery_soc = {0}".format(battery_soc))
        print("current net_load = {0}".format(net_load))

        # PV generation > building load, charge the battery
        if net_load < 0:
            print("PV generation more than load, charge battery")
            # charge if the battery is not full
            if battery_soc < self.max_battery_soc:
                # do not exceed maximum battery rate
                if abs(net_load) > self.max_battery_rate:
                    print("excess PV is greater than battery charge rate; changing charge rate to max_battery_rate={0}".format(self.max_battery_rate))
                    battery_setpoint = self.max_battery_rate
                else:
                    battery_setpoint = abs(net_load)
            else:
                print("Battery already full, new battery_setpoint = 0")
                battery_setpoint = 0
        # PV generation < building load, discharge the battery
        else:
            # discharge battery only if it isn't empty
            if battery_soc > self.min_battery_soc:
                if (-1*net_load) < self.min_battery_rate:
                    print("Current net load cannot be completely supported by battery, battery discharging at maximum rate={0}".format(self.min_battery_rate))
                    battery_setpoint = self.min_battery_rate
                else:
                    battery_setpoint = -1*net_load
            else:
                print("Battery already empty, new battery_setpoint = 0")
                battery_setpoint = 0

        time_now = pytz.timezone("UTC").localize(datetime.datetime.utcnow()).astimezone(pytz.timezone("America/Los_Angeles")).replace(tzinfo = None)
        if time_now.hour >= 0 and time_now.hour <= 5:
            hour_now = round(time_now.hour + time_now.minute/60 + time_now.second/3600, 2)
            print("low price time - charging battery so that it reaches maximum SOC by 6AM")
            battery_setpoint = (self.max_battery_soc - battery_soc)*self.battery_total_capacity/(6-hour_now)
            if battery_setpoint > self.max_battery_rate:
                battery_setpoint = self.max_battery_rate

        print("\n")
        print("New battery_setpoint = {0}".format(battery_setpoint))
        setpoint_df = pd.DataFrame(data={'battery_setpoint': [battery_setpoint]}, index=[end_time+datetime.timedelta(minutes=5)])
        setpoint_df.index.name='Time'
        setpoint_df = setpoint_df.resample('1T').mean().tz_localize("UTC")
        self.data_manager.set_setpoints(df=setpoint_df, overwrite=False)

if __name__ == '__main__':
    minute = -1

    controller = Baseline_Controller(config=baseline_config.get_config())
    while True:
        time.sleep(1)
        t = datetime.datetime.now()
        print(t)
        if (t.minute in [0,5,10,15,20,25,30,35,40,45,50,55]) and (t.minute != minute):
            minute = t.minute
            try:
                controller.generate_setpoints()
                print('Run ended ok.\n')
            except Exception as e :
               print('Run ended in error={0}'.format(str(e)))
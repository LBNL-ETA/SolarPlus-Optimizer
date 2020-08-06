import pandas as pd
import pytz
import datetime
import time
from baseline_controller import Baseline_Controller, baseline_config
from mpc_controller import MPC_Controller, mpc_config, tz_computer, islanding

tz_local = pytz.timezone("America/Los_Angeles")
tz_utc = pytz.timezone("UTC")

df = pd.read_csv("controller/test_schedule.csv", index_col=0)
df.start_time = pd.to_datetime(df.start_time)
df.end_time = pd.to_datetime(df.end_time)

minute = -1

baseline_controller = Baseline_Controller(config=baseline_config.get_config())
mpc_controller = MPC_Controller(mpc_config=mpc_config, tz_computer=tz_computer, islanding=islanding)

for index, row in df.iterrows():
    st = tz_local.localize(row['start_time']).astimezone(tz_utc)
    et = tz_local.localize(row['end_time']).astimezone(tz_utc)
    print("start_time = ", st)
    print("end time = ", et)
    is_baseline = bool(row['is_baseline'])
    
    time_now = tz_utc.localize(datetime.datetime.utcnow())
    run_minute = -1
    while st <= time_now and time_now <= et:
        if time_now.minute%5==0  and time_now.minute != run_minute:
            run_minute = time_now.minute
            if is_baseline:
                print("time_now = {0}; running baseline".format(time_now.strftime("%Y-%m-%d %H:%M:%S")))
                try:
                    baseline_controller.generate_setpoints()
                    print('Baseline run ended ok.\n')
                except Exception as e:
                    print('Baseline run ended in error={0}'.format(str(e)))
            else:
                print("time_now = {0}; runnign mpc".format(time_now.strftime("%Y-%m-%d %H:%M:%S")))
                try:
                    mpc_controller.run()
                    print('MPC run ended ok.\n')
                except Exception as e:
                    print('MPC run ended in error, error={0}'.format(str(e)))
        time.sleep(10)
        time_now = tz_utc.localize(datetime.datetime.utcnow())
        print("time_now = {0}".format(time_now.strftime("%Y-%m-%d %H:%M:%S")))
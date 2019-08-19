# Author: Anand Prakash <akprakash@lbl.gov>

##### client example ######
from data_client import Data_Client
import datetime
    

# create object of the data client
client = Data_Client()

# run time only used as suffix to filenames
run_time = datetime.datetime.now().strftime("%Y%m%dT%H%M")

# Make sure the start and end times are in this format
start_time = "2019/01/01 00:00:00"
end_time = "2019/12/31 23:59:59"

# subset of the variable list for each device
meter_variables = ['Demand', 'Freq', 'EnergySum', 'DemandApp', 'DemandMax', 'PowerSum']
thermostat_variables = ['active_cooling_setpt', 'active_heating_setpt', 'fan_status', 'fan', 'space_temp']
parker_controller_variables = ['OutputDefrostStatus', 'Setpoint', 'CurrentDefrostCounter', 'FansStatus', 'CabinetTemperature', 'ActiveSetpoint', 
                               'EvaporatorTemperature', 'ResistorsState', 'AuxiliaryTemperature', 'CompressorStatus', 'R4']


# get data from both all the wattnode meters
final_df = client.get_device_data(device_type='meters', start_time=start_time, end_time=end_time, variables=meter_variables)
final_df.to_csv("meter_readings_{0}.csv".format(run_time))

# get data from both the thermostats
final_df = client.get_device_data(device_type='thermostats', start_time=start_time, end_time=end_time, variables=thermostat_variables)
final_df.to_csv("thermostat_readings_{0}.csv".format(run_time))

# get data from both the refrigerator and freezer controllers
final_df = client.get_device_data(device_type='parker_controllers', start_time=start_time, end_time=end_time, variables=parker_controller_variables)
final_df.to_csv("parker_controller_readings_{0}.csv".format(run_time))

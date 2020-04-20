
from pyfmi import load_fmu

def load_battery_fmu(compiled_fmu=True):
    '''
    Load compiled FMU
    '''

    if compiled_fmu is False:
        battery_fmu = create_fmu()
    battery_fmu = 'simulation/SolarPlus_Batteries_Emulator.fmu'
    battery_emu = load_fmu(battery_fmu)

    return battery_emu

def simulate_fmu(start_time, final_time, power_setpoint):
    '''
    Simulate fmu that has already been compiled
    Parameters:
    power_setpoint: real power setpoint from a controller
    '''

    battery_emu = load_battery_fmu()
    res = battery_emu.simulate(start_time, final_time, input=power_setpoint)
    SOC_meas = res['SOC_meas']

    return SOC_meas, res

def plot_fmu(start_time, final_time, with_plot=True):

    import numpy as np
    import matplotlib.pyplot as plt

    t = np.linspace(start_time, final_time, num=144)
    u = np.cos(t/24)*10900
    u_traj = np.transpose(np.vstack((t,u)))
    power_setpoint = (['PSet'],u_traj)
    SOC_meas, res = simulate_fmu(start_time, final_time, power_setpoint)
    u_sim = res['PSet']
    time_sim = res['time']

    if with_plot:
        fig = plt.figure()
        plt.subplot(2,1,1)
        plt.plot(time_sim, u_sim)
        plt.subplot(2,1,2)
        plt.plot(time_sim, SOC_meas)
        plt.legend()
        plt.show()

def create_fmu():
    '''
    Create an fmu of the battery model in the emulator
    '''

    from pymodelica import compile_fmu
    import shutil

    model_name = 'SolarPlus.Batteries.Emulator'
    model_file = 'models/SolarPlus.mo'
    battery_fmu = compile_fmu(model_name, model_file)
    shutil.move('SolarPlus_Batteries_Emulator.fmu','simulation/SolarPlus_Batteries_Emulator.fmu')

    return battery_fmu

start_time = 0
final_time = 24*3600
plot_fmu(start_time, final_time)

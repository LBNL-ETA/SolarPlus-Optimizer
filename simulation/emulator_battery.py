
from pyfmi import load_fmu

class battery_emulator(object):

    def __init__(self, SOC_0, tz_name='UTC'):
        '''
        Constructor
        '''
        # needs to add configuration file for the battery.
        self.SOC_0 = SOC_0
        self.tz_name = tz_name


    def load_battery_fmu(self, compiled_fmu=True):
        '''
        Load compiled FMU
        '''

        if compiled_fmu is False:
            battery_fmu = self.create_fmu()
        else:
            battery_fmu = 'simulation/SolarPlus_Batteries_Emulator.fmu'
        battery_emu = load_fmu(battery_fmu)

        return battery_emu

    def simulate_fmu(self, start_time, final_time, inputs):
        '''
        Simulate fmu that has already been compiled
        Parameters:
        power_setpoint: real power setpoint from a controller
        '''

        battery_emu = self.load_battery_fmu()
        SOC_0 = battery_emu.get('simple.SOC_0')
        SOC_0 = self.SOC_0
        battery_emu.set('simple.SOC_0', SOC_0)
        res = battery_emu.simulate(start_time, final_time, inputs)
        # Measured SOC from the emulator
        SOC_meas = res['SOC_meas']
        # Measured PV generation from emulator
        PPv = res['PPv']
        # Power setpoint coming from the controller
        PSet_in = res['PSet']

        return SOC_meas, PSet_in, PPv, res

    def plot_fmu(self, start_time, final_time, with_plot=True):

        import numpy as np
        import matplotlib.pyplot as plt

        t = np.linspace(start_time, final_time, num=144)
        u1 = np.cos(t/24)*10000
        u2 = np.sin(t/24)*500
        u2[u2<0] = 0
        u_traj = np.transpose(np.vstack((t,u1,u2)))
        inputs = (['PSet', 'weaPoaPv'],u_traj)
        #poa_pv = (['weaPoaPv'], u2_traj)
        SOC_meas, PSet_in, PPv, res = self.simulate_fmu(start_time, final_time, inputs)
        time_sim = res['time']

        if with_plot:
            fig = plt.figure()
            plt.subplot(3,1,1)
            plt.plot(time_sim, PSet_in, label='Power setpoint')
            plt.legend()
            plt.subplot(3,1,2)
            plt.plot(time_sim, SOC_meas, label='SOC')
            plt.legend()
            plt.subplot(3,1,3)
            plt.plot(time_sim, PPv, label='PV generation')
            plt.legend()
            plt.show()

    def create_fmu(self):
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
emu = battery_emulator(SOC_0=0.5)
emu.plot_fmu(start_time, final_time)

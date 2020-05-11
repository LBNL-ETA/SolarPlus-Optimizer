from pyfmi import load_fmu
import asyncio
import numpy as np
import time

class Battery_Emulator(object):

    def __init__(self, config):
        '''
        Constructor
        '''
        self.config = config
        # needs to add configuration file for the battery.
        self.initial_SOC = self.config.get('inital_SOC', 0.5)
        self.rate = self.config.get('initial_rate', 10000)
        self.tz_name = self.config.get('tz_name', 'UTC')
        self.compiled_fmu = self.config.get('compiled_fmu', True)
        self.fmu_path = self.config.get('fmu_path', 'simulation/SolarPlus_Batteries_Emulator.fmu')

        self.battery = self.load_battery_fmu(compiled_fmu=self.compiled_fmu, initial_SOC=self.initial_SOC)
        self.simulate_options = self.battery.simulate_options()
        self.simulate_options['initialize'] = True

        self.update_step = self.config.get('update_step', 30)
        self.current_time = 0

    def load_battery_fmu(self, compiled_fmu=True, initial_SOC=0.5):
        '''
        Load compiled FMU
        '''

        if compiled_fmu is False:
            battery_fmu = self.create_fmu()
        else:
            battery_fmu = self.fmu_path
        battery_emu = load_fmu(battery_fmu)
        battery_emu.set('simple.SOC_0', initial_SOC)

        return battery_emu


    async def advance_time(self):
        while True:
            end_time = self.current_time + self.update_step
            power_setpoint = (['PSet'], np.array(
                [[self.current_time, self.rate],
                 [end_time, self.rate]]
            ))
            self.battery.simulate(self.current_time, end_time, power_setpoint, options=self.simulate_options)
            self.simulate_options['initialize'] = False
            self.current_time += self.update_step
            print(self.get_state())
            await asyncio.sleep(self.update_step)

    def get_state(self):
        return {'soc': self.battery.get('SOC_meas'), 'rate': self.battery.get('PSet')}

    def set_rate(self, rate):
        self.rate = rate
        print("new_rate: ", self.rate)

    async def start(self):
        self._task = asyncio.ensure_future(self.advance_time())

async def main():
    obj = Battery_Emulator({'initial_rate': 10000, 'fmu_path': 'SolarPlus_Batteries_Emulator.fmu'})
    await obj.start()

    obj.set_rate(10000)
    time.sleep(20)
    obj.set_rate(20000)
    time.sleep(20)
    obj.set_rate(-30000)
    time.sleep(20)
    obj.set_rate(2000)
    time.sleep(20)
#
# if __name__ == '__main__':
#     loop = asyncio.get_event_loop()
#     loop.run_forever(main())


    # def simulate_fmu(self, start_time, final_time, power_setpoint):
    #     '''
    #     Simulate fmu that has already been compiled
    #     Parameters:
    #     power_setpoint: real power setpoint from a controller
    #     '''
    #
    #     battery_emu = self.load_battery_fmu()
    #     SOC_0 = battery_emu.get('simple.SOC_0')
    #     SOC_0 = self.SOC_0
    #     battery_emu.set('simple.SOC_0', SOC_0)
    #     res = battery_emu.simulate(start_time, final_time, power_setpoint)
    #     # Measured SOC from the emulator
    #     SOC_meas = res['SOC_meas']
    #     # Power setpoint coming from the controller
    #     PSet_in = res['PSet']
    #
    #     return SOC_meas, PSet_in, res
    #
    # def plot_fmu(self, start_time, final_time, with_plot=True):
    #
    #     import numpy as np
    #     import matplotlib.pyplot as plt
    #
    #     t = np.linspace(start_time, final_time, num=144)
    #     u = np.cos(t/24)*10900
    #     u_traj = np.transpose(np.vstack((t,u)))
    #     power_setpoint = (['PSet'],u_traj)
    #     SOC_meas, PSet_in, res = self.simulate_fmu(start_time, final_time, power_setpoint)
    #     time_sim = res['time']
    #
    #     if with_plot:
    #         fig = plt.figure()
    #         plt.subplot(2,1,1)
    #         plt.plot(time_sim, PSet_in, label='Power setpoint')
    #         plt.legend()
    #         plt.subplot(2,1,2)
    #         plt.plot(time_sim, SOC_meas, label='SOC')
    #         plt.legend()
    #         plt.show()
    #
    # def create_fmu(self):
    #     '''
    #     Create an fmu of the battery model in the emulator
    #     '''
    #
    #     from pymodelica import compile_fmu
    #     import shutil
    #
    #     model_name = 'SolarPlus.Batteries.Emulator'
    #     model_file = 'models/SolarPlus.mo'
    #     battery_fmu = compile_fmu(model_name, model_file)
    #     shutil.move('SolarPlus_Batteries_Emulator.fmu','simulation/SolarPlus_Batteries_Emulator.fmu')
    #
    #     return battery_fmu

start_time = 0
final_time = 24*3600
emu = Battery_Emulator(SOC_0=0.5)
emu.plot_fmu(start_time, final_time)

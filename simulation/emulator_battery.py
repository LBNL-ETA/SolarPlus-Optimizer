
from pymodelica import compile_fmu
from pyfmi import load_fmu


model_name = 'SolarPlus.Building.Emulation.Store'
model_file = 'models/SolarPlus.mo'
battery_fmu = compile_fmu(model_name, model_file)
battery_emu = load_fmu(battery_fmu)

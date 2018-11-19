#Test Script for Venstar Driver


from venstar_driver import Venstar_Driver
#import requests
#import time
#import json

obj = Venstar_Driver("config.yaml")

print("+++++++++++++++++++++++++++++ Setting Cooling Setpoint ++++++++++++++++++++++++++++")
print(obj.query_info())
print("")
print("")
print("")
print("")
print("+++++++++++++++++++++++++++++ Get test ++++++++++++++++++++++++++++")
print(obj.set("cooling_setpoint",86))
print("")
print("")
print("")
print("")
print(obj.query_info())

#Test Script for Venstar Driver


from venstar_driver import Venstar_Driver
#import requests
#import time
#import json

obj = Venstar_Driver("config.yaml")
print("+++++++++++++++++++++++++++++ Get heattempmax only ++++++++++++++++++++++++++++")
print("heattempmax of thermostat:")
print(obj.get("heattempmax"))
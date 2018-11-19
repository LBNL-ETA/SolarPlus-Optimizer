#Test Script for Venstar Driver


from venstar_driver import Venstar_Driver
#import requests
#import time
#import json

obj = Venstar_Driver("config.yaml")

print(obj.query_info())
print("")
print("")
print("")
print("")
print("+++++++++++++++++++++++++++++ Setting Parameters ++++++++++++++++++++++++++++")
obj.controls(heattemp=53,cooltemp=82,mode=1,fan=1)
print("")
print("")
print("")
print("")
print(obj.query_info())
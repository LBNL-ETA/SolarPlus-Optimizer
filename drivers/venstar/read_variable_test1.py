#Test Script for Venstar Driver


from venstar_driver import Venstar_Driver
#import requests
#import time
#import json

obj = Venstar_Driver("config.yaml")
print("+++++++++++++++++++++++++++++ Query INFO ++++++++++++++++++++++++++++")
print(obj.query_info())
print("")
print("")
print("")
print("")
print("+++++++++++++++++++++++++++++ Query Sensors ++++++++++++++++++++++++++++")
print(obj.query_sensors())
print("")
print("")
print("")
print("")
print("+++++++++++++++++++++++++++++ Query  Runtimes ++++++++++++++++++++++++++++")
print(obj.query_runtimes())
print("")
print("")
print("")
print("")
print("+++++++++++++++++++++++++++++ Query  root ++++++++++++++++++++++++++++")
print(obj.query_root())
print("")
print("")
print("")
print("")
print("+++++++++++++++++++++++++++++ Query  alerts ++++++++++++++++++++++++++++")
print(obj.query_alerts())
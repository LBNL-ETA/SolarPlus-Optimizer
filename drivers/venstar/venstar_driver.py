### Venstar Driver
# @author : Andrew Shephard <akshephard@lbl.gov>


#TODO Add error handling
# Which from the api looks like....
"""
{
 "error": true,
 “reason”:”error reason”
}
"""
# Check the response and see if it has an error key in it and raise Exception
# and print the reason

# TODO Add better documentation... :/

"""
Version2: get_<param>() and set_<param>(value)
version3: get_<group_of_param>() and set_<group_of_param>
(dictionary of values): where the group of param's can be:
setpoints (parameter: {'cooling_setpoint': xx, 'heating_setpoint': xx} or
state (parameter: {'cooling_setpoint': xx, 'heating_setpoint': xx, override:xx, mode: xx, fan_mode:xx} again from xbos
"""

#for version 3, check the subsection "Slots" in the xbos doc

import requests
from influxdb import InfluxDBClient
import time
import json
import yaml
import logging



class Venstar_Driver(object):
    def __init__(self, config_file, config_section=None):
        if (config_section==None):
            venstar_section = 'venstar'
        #Initliaze Logging
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        with open(config_file) as f:
            # use safe_load instead load
            venstarConfig = yaml.safe_load(f)

        # Setup base host url of thermostat based on userconfig for endpoints
        self.HOST = venstarConfig[venstar_section]['host']
        self.HOST = "http://" + self.HOST

    def query_info(self):

        # Generate endpoint url
        url = self.HOST + "/query/info"

        # Send Get to endpoint http://VENSTAR_ADDRESS/query/sensors
        try:
            status=requests.request('get', url)      #http request
        except Exception as e:
            print(e)
            self.logger.error("unexpected error while sending request to API endpoint: " + url)

        # Convert response to json
        status=json.loads(status.text)
        return status

    def query_sensors(self):

        # Generate endpoint url
        url = self.HOST + "/query/sensors"

        # Send Get to endpoint http://VENSTAR_ADDRESS/query/sensors
        try:
            status=requests.request('get', url)      #http request
        except Exception as e:
            self.logger.error("unexpected error while sending request to API endpoint: " + url)

        # Convert response to json
        status=json.loads(status.text)
        return status

    def query_runtimes(self):

        # Generate endpoint url
        url = self.HOST + "/query/runtimes"

        # Send Get to endpoint http://VENSTAR_ADDRESS/query/runtimes
        try:
            status=requests.request('get', url)      #http request
        except Exception as e:
            self.logger.error("unexpected error while sending request to API endpoint: " + url)

        # Convert response to json
        status=json.loads(status.text)
        return status

    def query_alerts(self):

        # Generate endpoint url
        url = self.HOST + "/query/alerts"

        # Send Get to endpoint http://VENSTAR_ADDRESS/query/alerts
        try:
            status=requests.request('get', url)      #http request
        except Exception as e:
            self.logger.error("unexpected error while sending request to API endpoint: " + url)

        # Convert response to json
        status=json.loads(status.text)
        return status

    def query_root(self):

        # Generate endpoint url
        url = self.HOST + "/"

        # Send Get to endpoint http://VENSTAR_ADDRESS/
        try:
            status=requests.request('get', url)      #http request
        except Exception as e:
            self.logger.error("unexpected error while sending request to API endpoint: " + url)

        # Convert response to json
        status=json.loads(status.text)
        return status

    def controls(self,heattemp=None,cooltemp=None,mode=None,fan=None):
        # Both cooling and heating setpoint are required if one is to be changed
        # Set points are required when changing mode
        # Fan can be set by itself
        # Setpoints can be set without having mode or fan but they have to both
        # be present
        # TODO Test with pin
        # fan cannot be set to 1 if away is set to 1

        # Create URL Endpoint String
        url = self.HOST + "/control"

        # Generate data to be sent via POST request based on parameters
        payload = {}
        if mode != None:
            payload['mode']=mode
        if fan != None:
            payload['fan']=fan
        if heattemp != None:
            payload['heattemp']=heattemp
        if cooltemp != None:
            payload['cooltemp']=cooltemp
        """
        if pin != None:
            payload['pin']=pin
        """

        # Remove this later...
        print(payload)

        # Send POST request to Endpoint and check if there is an exception
        # Exception should only happen if there is a connection issue
        # API will send an error response if you send data with fields that
        # do not match the spec
        try:
            status=requests.request('get', url)      #http request
            r = requests.post(url, data=payload)
        except Exception as e:
            self.logger.error("unexpected error while sending POST to API endpoint: " + url)
        print(r.text)

        # May change this later need to decide where to do error handling
        return r

    def settings(self,tempunits=None,away=None,schedule=None):
        # Cannot set away to 0 and have schedule set to 1 in same payload
        # Can set them separately

        # Create URL Endpoint String
        url = self.HOST + "/settings"

        # Generate data to be sent via POST request based on parameters
        payload = {}
        if tempunits != None:
            payload['tempunits']=tempunits
        if away != None:
            payload['away']=away
        if schedule != None:
            payload['schedule']=schedule
        """
        if pin != None:
            payload['pin']=pin
        """
        # Remove this later...
        print(payload)

        # Send POST request to Endpoint and check if there is an exception
        # Exception should only happen if there is a connection issue
        # API will send an error response if you send data with fields that
        # do not match the spec
        try:
            r = requests.post(url, data=payload)
        except Exception as e:
            self.logger.error("unexpected error while sending POST to API endpoint: " + url)
        print(r.text)

        # May change this later need to decide where to do error handling
        return r

    def get(self,name):
        # Mention to Anand the issue with doc's regarding 'mode' and 'state'
        # Being incompatible
        # Disregard 3 on fan setting
        # Tested fan_state and heattempmax rest should work though
        # TODO  Add support for multiple sensors potentially in XBOS as well?
        # TODO Potentially change to some sort of standard XBOS values

        # Ask for all data from Venstar API, then return the specific field specified
        parse_data = self.query_info()
        ### XBOS common signals with Venstar ###
        if name == "temperature":
            return parse_data['spacetemp']
        elif name == "heating_setpoint":
            return parse_data['heattemp']
        elif name == "cooling_setpoint":
            return parse_data['cooltemp']
        elif name == "override":
            return parse_data['override']
        elif name == "relative_humidity":
            return parse_data['hum']
        elif name == "fan_state":
            return parse_data['fanstate']
        elif name == "fan_mode":
            return parse_data['fan']
        elif name == "mode":
            return parse_data['mode']
        elif name == "state":
            return parse_data['state']

        ### Venstar specifc fields ###
        # Assuming the name specified by the user is exactly the same as what is in
        # the Venstar API
        return parse_data[name]

    def get_temperature(self):
        return self.get("temperature")

    def get_heating_setpoint(self):
        return self.get("heating_setpoint")

    def get_cooling_setpoint(self):
        return self.get("cooling_setpoint")

    def get_override(self):
        return self.get("override")

    def get_relative_humidity(self):
        return self.get("relative_humidity")

    def get_fan_state(self):
        return self.get("fan_state")

    def get_fan_mode(self):
        return self.get("fan_mode")

    def get_mode(self):
        return self.get("mode")

    def get_state(self):
        return self.get("state")

    def get_xbos_param(self):
        parse_data = self.query_info()
        obj = {}
        obj['temperature'] = parse_data['spacetemp']
        obj['heating_setpoint'] = parse_data['heattemp']
        obj['cooling_setpoint'] = parse_data['cooltemp']
        obj['override'] = parse_data['override']
        obj['relative_humidity'] = parse_data['hum']
        obj['fan_state'] = parse_data['fanstate']
        obj['fan_mode'] = parse_data['fan']
        obj['mode'] = parse_data['mode']
        obj['state'] = parse_data['state']
        return obj


    def set(self,name, value):
        """
        Possible values to set
        heating_setpoint
        cooling_setpoint
        mode
        fan_mode
        """
        if name == "heating_setpoint":
            prev_cool_temp = self.get("cooling_setpoint")
            response = self.controls(heattemp=value,cooltemp=prev_cool_temp)
        elif name == "cooling_setpoint":
            prev_heat_temp = self.get("heating_setpoint")
            response = self.controls(heattemp=prev_heat_temp,cooltemp=value)
        elif name == "fan_mode":
            response = self.controls(fan=value)
        elif name == "mode":
            prev_cool_temp = self.get("cooling_setpoint")
            prev_heat_temp = self.get("heating_setpoint")
            response = self.controls(heattemp=prev_heat_temp,cooltemp=prev_cool_temp,mode=value)
        return response

    def set_group_parm(self,obj):
        self.set(heating_setpoint,obj[heating_setpoint])
        self.set(cooling_setpoint,obj[cooling_setpoint])
        self.set(fan_mode,obj[fan_mode])
        self.set(mode,obj[mode])

    def set_cooling_setpoint(self, value):
        return self.set("cooling_setpoint",value)

    def set_heating_setpoint(self, value):
        return self.set("heating_setpoint",value)

    def set_fan_mode(value):
        return self.set("fan_mode",value)

    def set_mode(value):
        return self.set("mode",value)

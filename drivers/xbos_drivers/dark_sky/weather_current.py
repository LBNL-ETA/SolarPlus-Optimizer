from pyxbos.driver import *
from pyxbos import weather_station_pb2
import os,sys
import json
import requests
import yaml
import argparse
import logging

class WeatherCurrentDriver(Driver):
    def setup(self, cfg):
        self.baseurl = cfg['darksky']['url']
        self.apikey = cfg['darksky']['apikey']
        self.coords = cfg['darksky']['coordinates']
        self.url = self.baseurl + self.apikey + '/' + self.coords
        self.service_name = cfg['service_name']

    def read(self, requestid=None):
        response = requests.get(self.url)
        json_data = json.loads(response.text)
        if 'currently' not in json_data: return

        logging.info("currently {0}".format(json_data['currently']))
        print(json_data['currently'])
        output = {}
        for key, value in json_data['currently'].items():
            output[key] = value

        #print(json_data['currently'])
        if 'humidity' in output:
            output['humidity'] *= 100 # change from decimal to percent

        msg = xbos_pb2.XBOS(
            XBOSIoTDeviceState = iot_pb2.XBOSIoTDeviceState(
                time = int(time.time()*1e9),
                weather_station = weather_station_pb2.WeatherStation(
                    time  =   types.Int64(value=output.get('time',None)),
                    icon  =  output.get('icon',None),
                    nearestStormDistance  =   types.Double(value=output.get('nearestStormDistance',None)),
                    nearestStormBearing  =   types.Double(value=output.get('nearestStormBearing',None)),
                    precipIntensity  =   types.Double(value=output.get('precipIntensity',None)),
                    precipIntensityError  =   types.Double(value=output.get('precipIntensityError',None)),
                    precipProbability  =   types.Double(value=output.get('precipProbability',None)),
                    precipType  =  output.get('precipType',None),
                    temperature  =   types.Double(value=output.get('temperature',None)),
                    apparentTemperature  =   types.Double(value=output.get('apparentTemperature',None)),
                    dewPoint  =   types.Double(value=output.get('dewPoint',None)),
                    humidity  =   types.Double(value=output.get('humidity',None)),
                    pressure  =   types.Double(value=output.get('pressure',None)),
                    windSpeed  =   types.Double(value=output.get('windSpeed',None)),
                    windGust  =   types.Double(value=output.get('windGust',None)),
                    windBearing  =   types.Double(value=output.get('windBearing',None)),
                    cloudCover  =   types.Double(value=output.get('cloudCover',None)),
                    uvIndex  =   types.Double(value=output.get('uvIndex',None)),
                    visibility  =   types.Double(value=output.get('visibility',None)),
                    ozone  =   types.Double(value=output.get('ozone',None)),
                )
            )
        )
        self.report(self.service_name, msg)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("config_file", help="config file with api key as well as namespace")
    args = parser.parse_args()
    config_file = args.config_file

    with open(config_file) as f:
        driverConfig = yaml.safe_load(f)

    xbosConfig = driverConfig['xbos']
    waved = xbosConfig.get('waved', 'localhost:777')
    wavemq = xbosConfig.get('wavemq', 'locahost:4516')
    namespace = xbosConfig.get('namespace')
    base_resource = xbosConfig.get('base_resource')
    service_name = xbosConfig.get('service_name')
    entity = xbosConfig.get('entity')
    rate = xbosConfig.get('rate')
    driver_id = xbosConfig.get('id', 'darksky-driver')

    darkskyConfig = driverConfig['dark_sky']
    url = darkskyConfig.get('url', 'https://api.darksky.net/forecast/')
    api = darkskyConfig.get('api')
    coordinates = darkskyConfig.get('latlong')

    xbos_cfg = {
        'waved': waved
        'wavemq': wavemq,
        'namespace': namespace,
        'base_resource': base_resource,
        'entity': entity,
        'id': driver_id,
        'rate': rate, 
        'service_name_map': service_name_map,
        
        'darksky': {
            'apikey': api,
            'url': url,
            'coordinates': latlong
        }
    }

    logging.basicConfig(level="INFO", format='%(asctime)s - %(name)s - %(message)s')
    current_driver = WeatherCurrentDriver(cfg)
    current_driver.begin()

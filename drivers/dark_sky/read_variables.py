import requests
import yaml
import json
import datetime
import pytz

# https://api.darksky.net/forecast/763827c188fa2c8c4cca914f16caf2d0/40.5301,-124.0000

if __name__== "__main__":
	with open("config.yaml") as fp:
		config = yaml.safe_load(fp)["dark_sky"]

	apikey = config["api"]
	url = config["url"]
	lat = config["lat"]
	lng = config["lng"]

	req_url = "{0}/{1}/{2},{3}".format(url, apikey, lat, lng)

	rsp = requests.get(req_url)
	op = json.loads(rsp.text)
	
	print("Current values:")
	print(op['currently'])
	print()

	print("Hourly forecasts")
	hourly = op["hourly"]["data"]
	for i in range(len(hourly)):
		time = datetime.datetime.utcfromtimestamp(hourly[i]["time"]).replace(tzinfo=datetime.timezone.utc).astimezone(pytz.timezone("America/Los_Angeles")).strftime("%Y-%m-%d %H:%M:%S %Z")
		temperature = hourly[i]['temperature']
		humidity = hourly[i]['humidity']*100
		cloudCover = hourly[i]['cloudCover']
		new_dict = {
			'time': time,
			'temperature': temperature, 
			'humidity': humidity,
			'cloudCover': cloudCover
		}
		print(i,": ", new_dict)
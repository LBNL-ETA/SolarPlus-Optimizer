from venstar_driver import Venstar_Driver
import time
import json
import argparse

def main(config,output_file):
	obj = Venstar_Driver("config.yaml")
	output = {}
	count = 0
	filename = output_file
	with open(filename, 'w') as outfile:
		outfile.write('[')
		while(1):
			print("Recording data")
			output = obj.query_info()
			output['time'] = int(time.time())
			output['increment'] = count
			output['runtime'] = obj.query_runtimes()
			json.dump(output, outfile)
			print(output['spacetemp'], output['heattemp'], output['cooltemp'])
			time.sleep(1)
			outfile.write(',\n')
			count += 1
	obj.kill_modbus()


def cleanup(filename):
	outfile = open(filename, "a")
	outfile.write("]")
	outfile.close()
	print("Closing file and saving results")

if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument("config", help="config file")
	parser.add_argument("output_file", help="config file")

	args = parser.parse_args()
	config_file = args.config
	filename = args.output_file
	try:
		main(config_file,filename)
	except KeyboardInterrupt:
		cleanup(filename)
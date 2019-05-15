from pyxbos.mortard import MortarClient
import pymortar
import yaml
from flask import Flask, request
import datetime
import json


class XBOS_Web_Server:

    def __init__(self, name="xbos_server", config_filename="access_config_testing.yaml", section="mortar_config"):
        with open(config_filename, "r") as fp:
            config = yaml.safe_load(fp)[section]

        self.client = MortarClient({
            'namespace': config["namespace"],
            'wave': config["wave"],
            'entity': config["entity"],
            'prooffile': config["prooffile"],
            'grpcservice': config["grpcservice"],
            'address': config["address"],
        })

        self.app = Flask(name)

    def get_data(self):
        req = request.get_json()
        uuid = req['uuid']
        time_now = datetime.datetime.now()
        start = req.get('start', (time_now - datetime.timedelta(hours=24)).strftime("%Y-%m-%dT%H:%M:%SZ"))
        end = req.get('end', time_now.strftime("%Y-%m-%dT%H:%M:%SZ"))
        window = req.get('window', '5m')
        sites = req.get('site', ['blr'])
        agg_fn = req.get('agg', 'MEAN')
        agg_fn_map = {
            'MEAN': pymortar.MEAN,
            'MIN': pymortar.MIN,
            'MAX': pymortar.MAX,
         }
        agg = agg_fn_map[agg_fn]

        req = pymortar.FetchRequest(
            sites=sites,
            dataFrames=[
                pymortar.DataFrame(
                    name="timeseries_data",
                    aggregation=agg,
                    window=window,
                    uuids=[uuid]
                )
            ],
            time=pymortar.TimeParams(
                start=start,
                end=end,
            )
        )
        result = self.client.fetch(req)
        return json.dumps(
            {
                "data": result["timeseries_data"].to_json()
            }
        )

    def run(self):
        self.app.add_url_rule('/get_data', 'get_data', self.get_data)
        self.app.run()

web_server = XBOS_Web_Server()
web_server.run()
# -*- coding: utf-8 -*-
"""
This module implements the REST API used to interact with the data manager.  
The API is implemented using the ``flask`` package.  

"""

# GENERAL PACKAGE IMPORT
# ----------------------
from flask import Flask
from flask_restful import Resource, Api, reqparse
# ----------------------

# DATA XBOS AND OTHER PACKAGES
# ----------------
import pandas as pd

# FLASK REQUIREMENTS
# ------------------
app = Flask(__name__)
api = Api(app)
# ------------------

# DEFINE ARGUMENT PARSERS
# -----------------------
# ``setpoints`` interface
parser_setpoints = reqparse.RequestParser()
parser_setpoints.add_argument('Trtu')
parser_setpoints.add_argument('Tref')
# ``data`` interface
parser_data = reqparse.RequestParser()
parser_data.add_argument('variable')
# -----------------------

# DEFINE REST REQUESTS
# --------------------
class SetSetpoints(Resource):
    '''Interface to set setpoints.'''    
    
    def post(self):
        '''POST request with input data to set setpoints.'''
        u = parser_setpoints.parse_args()
        y = {'Trtu' : u['Trtu']}
        return y

class GetData(Resource):
    '''Interface to test case simulation step size.'''
    
    def post(self):
        '''POST request with input data to get specified data.'''
        u = parser_data.parse_args()
        xbos_id = u['variable'] # get xbos id somehow from variable name
        # Create dataframe (TODO: Get from XBOS)
        index = pd.date_range('1/1/2019', '1/2/2019', freq='5T')
        data = list(range(len(index)))
        df = pd.DataFrame(data=data, index=index)
        # Make json
        y = df.to_json(orient='columns')
        print(y)
        return y
# --------------------
        
# ADD REQUESTS TO API WITH URL EXTENSION
# --------------------------------------
api.add_resource(SetSetpoints, '/setsetpoints')
api.add_resource(GetData, '/getdata')
# --------------------------------------

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
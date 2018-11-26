#import configparser
import pandas as pd
import numpy as np
from influxdb import InfluxDBClient
from influxdb import DataFrameClient
import yaml

'''
Two dataframe formats are accepted both are shown below:
                       time              ap_name  AP_count             parse_ap_name building_number floor room  test_field
0 2016-04-01 07:00:00+00:00  ap135-100-103d-r177       1.0  [ap135, 100, 103d, r177]             100     1  03d         1.0
1 2016-04-01 07:00:00+00:00   ap135-100-121-r177       3.0   [ap135, 100, 121, r177]             100     1  121         1.0
2 2016-04-01 07:00:00+00:00   ap135-100-139-r177       6.0   [ap135, 100, 139, r177]             100     1  139         1.0
3 2016-04-01 07:00:00+00:00   ap135-100-140-r177       5.0   [ap135, 100, 140, r177]             100     1  140         1.0
4 2016-04-01 07:00:00+00:00  ap135-100-149b-r177       1.0  [ap135, 100, 149b, r177]             100     1  49b         1.0

The same dataframe can also be given as where the index is the time:
                           AP_count              ap_name building_number floor room  test_field
2016-04-01 07:00:00+00:00         1  ap135-100-103d-r177             100     1  03d           1
2016-04-01 07:00:00+00:00         5   ap135-100-150-r177             100     1  150           1
2016-04-01 07:00:00+00:00         3   ap135-100-121-r177             100     1  121           1
2016-04-01 07:00:00+00:00         5   ap135-100-140-r177             100     1  140           1
2016-04-01 07:00:00+00:00         1  ap135-100-149b-r177             100     1  49b           1

This is converted to the following json before being given to DataFrameClient during write
[
  {
    'fields': {
        'AP_count': 1.0,
        'test_field': 1.0
        },
    'time': Timestamp('2016-04-01 07:00:00+0000', tz='UTC'),
    'tags': {
        'floor': '1',
        'building_number': '100',
        'ap_name': 'ap135-100-103d-r177',
        'room': '03d'
        },
    'measurement': 'wifi_data9'
    },
  {
    'fields': {
        'AP_count': 3.0,
        'test_field': 1.0
        },
    'time': Timestamp('2016-04-01 07:00:00+0000', tz='UTC'),
    'tags': {
        'floor': 1,
        'building_number': '100',
        'ap_name': 'ap135-100-121-r177',
        'room': '121'
        },
    'measurement': 'wifi_data9'
    },
  {
    'fields': {
        'AP_count': 6.0,
        'test_field': 1.0
        },
    'time': Timestamp('2016-04-01 07:00:00+0000', tz='UTC'),
    'tags': {
        'floor': 1,
        'building_number': '100',
        'ap_name': 'ap135-100-139-r177',
        'room': '139'
        },
  'measurement': 'wifi_data9'
    },
  {
    'fields': {
        'AP_count': 5.0,
        'test_field': 1.0
        },
    'time': Timestamp('2016-04-01 07:00:00+0000', tz='UTC'),
    'tags': {
        'floor': 1,
        'building_number': '100',
        'ap_name': 'ap135-100-140-r177',
        'room': '140'
        },
    'measurement': 'wifi_data9'},
  {
    'fields': {
        'AP_count': 1.0,
        'test_field': 1.0
        },
    'time': Timestamp('2016-04-01 07:00:00+0000', tz='UTC'),
    'tags': {
        'floor': '1',
        'building_number': '100',
        'ap_name': 'ap135-100-149b-r177',
        'room': '49b'
        },
    'measurement': 'wifi_data9'
    }
 ]
Time can be specified in epoch time or Influx format

When making queries, identifiers may be put into Double quotes depending on the
characters they contain. String literals i.e. tag values must be in single quotes!
'''


def transform_to_dict(s, tags):
    '''
    Returns a dictionary where the keys are passed in as a list and the values
    are obtained from the apply function as a row
    '''
    dic = {}
    for tag in tags:
        dic[tag] = s[tag]
    return dic


class Influx_Dataframe_Client(object):
    #Connection details
    host = ""
    port = ""
    username = ""
    password = ""
    database = ""
    use_ssl= False
    verify_ssl_is_on = False
    #clients for influxDB both DataFrameClient and the InfluxDBClient
    client = None
    df_client = None
    data = None


    def __init__(self, config_file,db_section=None):
        '''
        Constructor reads credentials from config file and establishes a connection
        '''
        #read from config file and establish connection to server
        with open(config_file) as f:
            # use safe_load instead load
            influxConfig = yaml.safe_load(f)

        if(db_section == None):
            db_section = 'DB_config'


        self.host = influxConfig[db_section]['host']
        self.username = influxConfig[db_section]['username']
        self.password = influxConfig[db_section]['password']
        self.database = influxConfig[db_section]['database']
        self.protocol = influxConfig[db_section]['protocol']
        self.port = influxConfig[db_section]['port']
        self.use_ssl = influxConfig[db_section]['use_ssl']
        self.verify_ssl_is_on = influxConfig[db_section]['verify_ssl_is_on']
        self.__make_client()



    def __make_client(self):
        '''
        This function is not necessary for the user.

        Setup client both InfluxDBClient and DataFrameClient
        DataFrameClient is for queries and InfluxDBClient is for writes
        Not needed by user
        '''

        self.client = InfluxDBClient(host=self.host, port=self.port,
                    username=self.username, password=self.password,
                    database=self.database,ssl=self.use_ssl, verify_ssl=self.verify_ssl_is_on)
        self.df_client = DataFrameClient(host=self.host, port=self.port,
                    username=self.username, password=self.password,
                    database=self.database,ssl=self.use_ssl, verify_ssl=self.verify_ssl_is_on)

    def __build_json(self,data, tags, fields, measurement):
        '''
        This function is not necessary for the user.

        Builds json dictionary list out of dataframe given in the format expected
        by InfluxDBClient. Both tags and fields need to be lists which include
        the columns in the dataframe that are going to be included in the tags
        and fields dictionary
        '''

        data['measurement'] = measurement
        data["tags"] = data.loc[:,tags].apply(transform_to_dict, tags=tags, axis=1)
        data["fields"] = data.loc[:,fields].apply(transform_to_dict, tags=fields, axis=1)
        json = data[["measurement","time", "tags", "fields"]].to_dict("records")

        return json

    def __post_to_DB(self,json,database=None):
        '''
        This function is necessary for the user.

        Sends json dictionary list to specified database to InfluxDBClient
        '''
        ret = self.client.write_points(json,database=database,batch_size=16384)
        return ret



    def expose_influx_client(self):
        '''
        Expose InfluxDBClient to user so they can utilize all functions of
        InfluxDBClient if functionality is not provided by
        Influx_Dataframe_Client module
        '''

        return self.client

    def expose_data_client(self):
        '''
        Expose DataFrameClient to user so they can utilize all functions of
        DataFrameClient if functionality is not provided by
        Influx_Dataframe_Client module
        '''

        return self.df_client


    def write_dataframe(self,data,tags,fields,measurement,database=None):
        '''
        Write a dataframe to the specified measurement, the user needs to
        specify the tags and fields that are to be included in the measurement
        as lists
        '''

        #set default database
        if (database == None):
            database = self.database


        if 'time' not in data.columns: #check to see if the time column is present
            data.index.name = 'time' #change the index to name to time
            data = data.reset_index() # give seqeuential index to dataframe

        #Turn dataframe into correct json format as described in beginning comments
        json = self.__build_json(data,tags,fields,measurement)

        ret = self.__post_to_DB(json,database)

        return ret

    def write_csv(self,csv_fileName,tags,fields,measurement,database=None):
        '''
        Take in csv file and upload to database. User must specify list of tags
        and a list of fields as well as the csv file name. Database is optional
        by default the database specified by the client will be used
        '''

        #set default database
        if (database == None):
            database = self.database

        data = pd.read_csv(csv_fileName)
        ret = self.write_dataframe(data,tags,fields,measurement,database)

        return ret

    def write_json(self,json,database=None):
        '''
        Take in json in the form of a list of dictionaries or a single dictionary
        and upload to database. User must specify list of tags and a list of fields as well as the csv file name. Database is optional
        by default the database specified by the client will be used
        '''

        #set default database
        if (database == None):
            database = self.database

        #check to see if json is a list of dictionaries or a single dictionary
        if isinstance(json, list):
            ret = self.__post_to_DB(json,database)
        else:
            json = [json]
            ret = self.__post_to_DB(json,database)

        return ret

    def list_DB(self):
        '''
        Returns a list of all the names of the databases on the influxDB server
        '''
        list_to_return = []
        DB_dict_list = self.client.get_list_database()

        for x in range(len(DB_dict_list)):
            list_to_return.append(DB_dict_list[x]['name'])

        return list_to_return

    def list_retention_policies(self):

        '''
        Returns a list of dictionaries with all the databases
        on the influxDB server and their associated retention policies
        '''
        DB_list = self.list_DB()
        dict_list = []
        for x in range(len(DB_list)):
            temp_dict = {}
            temp_dict[DB_list[x]] = self.client.get_list_retention_policies(DB_list[x])
            dict_list.append(temp_dict)
        return dict_list

    def query_data(self,query):
        '''
        Sends the specified query string to the specified database using
        InfluxDBClient the query must be in Influx Query Language
        '''
        df = self.df_client.query(query, database='wifi_data8',chunked=True, chunk_size=256)
        return df

    def query(self, query, use_database = None):
        '''
        Sends the specified query string to the specified database using the
        DataframeClient the query must be in Influx Query Language returns a
        dataframe
        '''
        query_result = self.client.query(query, database=use_database)
        return query_result.raw

    def show_meta_data(self, database, measurement):
        '''
        Returns a list of TAG KEYS for specified measurement in specified database
        Equivalent query is below
        SHOW TAG KEYS FROM "MEASUREMENT_ARGUMENT"
        '''

        result_list = []
        #generate query string and make query
        query_string = 'SHOW TAG KEYS FROM ' +'\"' + measurement + "\""
        query_result = self.client.query(query_string, database=database)
        #add all of the tag values into a list to be returned
        #query result is a generator
        for temp_dict in query_result.get_points():
            result_list.append(temp_dict['tagKey'])
        return result_list

    def get_meta_data(self,database, measurement,tag):
        '''
        Returns a list of TAG VALUES for specified measurement in specified database
        Equivalent query is below
        SHOW TAG VALUES FROM "MEASUREMENT_ARGUMENT" WITH KEY IN = "TAG_ARGUMENT"
        '''
        result_list = []
        #generate query string and make query
        query_string = 'SHOW TAG VALUES FROM ' + '\"' + measurement + '\"' + 'WITH KEY = \"' + tag + '\"'
        query_result = self.client.query(query_string, database=database)

        #add all of the tag values into a list to be returned
        #query result is a generator
        for temp_dict in query_result.get_points():
            result_list.append(temp_dict['value'])

        return result_list
    def get_meta_data_time_series(self,database, measurement, tags,start_time=None,end_time=None):
        '''
        Returns tags along with the time stamps
        '''

        #get all data with from measurement
        df = self.specific_query(database,measurement,start_time=start_time,end_time=end_time)
        return df[tags]

    def specific_query(self,database,measurement,fields=None,start_time=None,end_time=None,tags=None,values=None,groupList=None,groupTime=None):
        '''
        This function returns a dataframe with the results of the specified query
        the query is built using the parameters provided by the user and
        formatted into Influx Query Language. All fields are optional except the
        database and measurement parameter. This function always returns a
        dataframe even if the response has no results
        '''
        tag_string = ""
        time_string = ""
        group_string = ""
        df = {}
        #Create base query with fields and measurement
        query_string = "SELECT "
        if (fields == None):
            query_string = query_string + '* '
        else:
            for x in range(len(fields)):
                if (x > 0):
                    query_string = query_string + " ,"
                query_string = query_string + "\"" + fields[x] + "\""
        query_string = query_string + " FROM \"" + measurement + "\""

        #Create time portion of query if it is specified
        if (start_time != None or end_time != None ):
            if (start_time != None):
                #Must have a start_time for our query
                #Check to see format of time that was specified
                time_string = time_string + "time > "
                if type(end_time) == str:
                    time_string = time_string + "\'" + start_time + '\''
                if(type(end_time) == int):
                    time_string = time_string + str(start_time)

            if (end_time != None):
                #Must have a end_time for our query
                #Check to see format of time that was specified
                if (time_string != ""):
                    time_string = time_string + " AND "
                time_string = time_string + "time < "

                if type(end_time) == str:
                    time_string = time_string + "\'" + end_time + '\''

                if type(end_time) == int:
                    time_string = time_string + str(end_time)


        #Create tag portion of query if it is specified
        if (tags != None and values != None):
            try:
                if (len(tags) != len(values)):
                    print("Tags and values do not match raise exception later!")
                    raise BaseException
                else:
                    tag_string = ""
                    for x in range(len(tags)):
                        if (x > 0):
                            tag_string = tag_string + ' AND '
                        tag_string = tag_string + '\"' + tags[x] + "\" = \'" + values[x] + "\'"
            except BaseException:
                print("Tags and values do not match")
                return pd.DataFrame()
        if (groupList != None):
            query_string = query_string + "GROUP BY"
            for x in range(len(groupList)):
                if (x > 0):
                    query_string = query_string + ","
                if (groupList[x] == "time"):
                    query_string = query_string + "time(" + groupTime + ")"
                else:
                    query_string = query_string + "\""+groupList[x]+"\""

        #Add optional parts of query
        if (time_string != "" or tag_string != ""):
            query_string = query_string + " WHERE "
            if (time_string != ""):
                query_string = query_string + time_string
            if (tag_string != ""):
                if (time_string != ""):
                    query_string = query_string + " AND "
                query_string = query_string + tag_string
        if (group_string != ""):
            query_string = query_string + group_string

        print(query_string)

        df = self.df_client.query(query_string, database=database,chunked=True, chunk_size=256)

        if (measurement in df):
            return df[measurement]
        else:
            #Must have an empty result make empty dataframe
            df = pd.DataFrame()
        return df

    def delete_based_on_time(self,database,measurement,start_time=None,end_time=None):
        '''
        Delete data from measurement. If no time is specified then all data will
        be deleted from the measurement.
        '''
        time_string = ""
        query_string = "DELETE FROM %s "%measurement

        if (start_time != None):
            #Must have a start_time for our query
            #Check to see format of time that was specified
            time_string = time_string + "time > "
            if type(end_time) == str:
                time_string = time_string + "\'" + start_time + '\''
            if type(end_time) == int:
                time_string = time_string + str(start_time)

        if (end_time != None):
            #Must have a end_time for our query
            #Check to see format of time that was specified
            if (time_string != ""):
                time_string = time_string + " AND "
            time_string = time_string + "time < "

            if type(end_time) == str:
                time_string = time_string + "\'" + end_time + '\''

            if type(end_time) == int:
                time_string = time_string + str(end_time)

        if time_string != "":
            query_string = query_string + " WHERE "
            if (time_string != ""):
                query_string = query_string + time_string

        # print(query_string)
        df = self.df_client.query(query_string, database=self.database,chunked=True, chunk_size=256)

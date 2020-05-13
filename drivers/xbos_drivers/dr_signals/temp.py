st = '2019-12-18T20:00:00'



import pytz, datetime
local = pytz.timezone("US/Pacific")
naive = datetime.datetime.strptime('2019-12-18T20:00:00', '%Y-%m-%dT%H:%M:%S')
# naive = datetime.datetime.strptime ("2001-2-3 10:11:12", "%Y-%m-%d %H:%M:%S")
local_dt = local.localize(naive, is_dst=None)
utc_dt = local_dt.astimezone(pytz.utc)
print(utc_dt.strftime ("%Y-%m-%dT%H:%M:%S"))
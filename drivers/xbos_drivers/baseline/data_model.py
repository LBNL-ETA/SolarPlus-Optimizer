import datetime
from pandas.tseries.holiday import USFederalHolidayCalendar as calendar

class DataModel:
    """ Collection of 10/10 10/15 15/20 models... """

    def __init__(self, data, event_day, init_args, rmse=None):
        self.raw_data = data
        self.data = self.raw_data.copy()
        self.event_day = event_day
        self.X = init_args[0]
        self.Y = init_args[1]

    def get_X_in_Y_baseline(self):
        self.data = self.remove_event_day()
        self.data = self.remove_weekend_holidays_nan()
        self.data_y = self.get_last_y_days(data)
    
    def remove_event_day(self):
        try:
            data = self.data[~(self.data.index.date == self.event_day)]
            return data
        except Exception as e:
            print("Error in remove_event_day: ", e)

    def remove_weekend_holidays_nan(self):
        no_weekend = ~((self.data.index.weekday == 5) | (self.data.index.weekday == 6))
        no_nan = ~self.data.isna().all(axis=1) # remove if has any NaN for any hour

        cal = calendar()
        start = datetime.datetime.strftime(self.data.index.min(), "%Y-%m-%d")
        end = datetime.datetime.strftime(self.data.index.max(), "%Y-%m-%d")
        hol_cal = cal.holidays(start=start, end=end)
        no_hol = ~self.data.index.isin(hol_cal) # remove if it is a national holiday

        return self.data[no_weekend & no_hol & no_nan]

    def get_last_Y_days(self):
        assert self.data.shape[0] >= Y, "{} not enough data for {} days".format(self.event_day, self.Y)
        try:
            start = self.data.index[0]
            data = self.data[start:self.event_day]
            data = data.sort_index(ascending=False).iloc[0:self.Y, :]
            return data
        except Exception as e:
            print("Error in get_last_Y_days: ", e)

    def _get_X_in_Y(self, data, power_data, X=None, event_start_h=14, event_end_h=18, 
                    weather_event_data=None, include_last=False, 
                    weather_mapping=False, weather_data=None, method='max'):
        #choses the highest X days out of Y days (if weather_mapping is true, it choses the days with the highest OAT values)
        if not X:
            X = power_data.shape[0]
        cols = np.arange(event_start_h, event_end_h+include_last*1)

        if weather_mapping==True:
            if method=='proximity': #chooses x days based on how close the weather is
                rows=np.shape(weather_data)[0]
                weather_event_day=weather_event_data
                for i in range(rows-1):
                    weather_event_data=weather_event_data.append(weather_event_day, ignore_index=True)

                weather_event_data=weather_event_data[cols]
                weather_event_data.index=weather_data[cols].index
                x_days=abs(weather_event_data-weather_data[cols]).sum(axis=1).sort_values(ascending=True)[0:X].index

            else:
                x_days=weather_data[cols].sum(axis=1).sort_values(ascending=False)[0:X].index
        else:
            x_days = power_data[cols].sum(axis=1).sort_values(ascending=False)[0:X].index
        return data[data.index.isin(x_days)], x_days


    """
    if method='proximity' (and weather-mapping=true), then it chooses the X days that are closest to the weather in the event day,
    if method='max' it chooses the hottest x days out of y days.
    """
    def get_X_in_Y_baseline(data, weather_pivot, event_day,PDP_dates,
                            event_index,
                            X=3,
                            Y=10,
                            event_start_h=12,
                            event_end_h=18,
                            include_last=False,
                            adj_ratio=True,
                            min_ratio=1.0,
                            max_ratio=1.3,
                            sampling="quarterly", weather_mapping=False, method='max'):

        event_data= data[data.index.date == event_day]
        data = _remove_event_day(data, event_index,PDP_dates)
        data = _remove_WE_holidays_NaN(data)
        weather_event_data=weather_pivot[weather_pivot.index.date == event_day]
        weather_data=_remove_event_day(weather_pivot, event_index, PDP_dates)
        weather_data = _remove_WE_holidays_NaN(weather_data)
        data_y =_get_last_Y_days(data, event_index, Y)

        days=data_y.index
        weather_data=_get_last_Y_days(weather_data, event_index, Y)

        data_x, x_days = _get_X_in_Y(data, power_data=data_y,
                        X=X,
                        event_start_h=event_start_h,
                        event_end_h=event_end_h,
                            weather_event_data=weather_event_data,
                        include_last=include_last, weather_mapping=weather_mapping, weather_data=weather_data, method=method)

        if adj_ratio:

            ratio = _get_adj_ratio(data_x, event_data,
                                event_start_h=event_start_h,
                                min_ratio=min_ratio,
                                max_ratio=max_ratio)
        else:
            ratio = 1
        data_x = (data_x.mean()*ratio).to_frame() # baseline is the average of the days selected
        data_x.columns = ["baseline"]
        return data_x, days, event_data.T, x_days, ratio
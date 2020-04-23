import pandas as pd
from sklearn import preprocessing


class Process_Data:
    """ This class preprocesses a dataframe according to user specification. """

    def __init__(self, df):
        """ Constructor.
        This class stores the original data (passed in through the constructor) and the preprocessed data.
        Parameters
        ----------
        df  : pd.DataFrame()
            Dataframe to preprocess.
        """
        self.original_data = df
        self.processed_data = pd.DataFrame()

    def add_degree_days(self, col='OAT', hdh_cpoint=65, cdh_cpoint=65):
        """ Adds Heating & Cooling Degree Hours.
        Parameters
        ----------
        col         : str
            Column name which contains the outdoor air temperature.
        hdh_cpoint  : int
            Heating degree hours. Defaults to 65.
        cdh_cpoint  : int
            Cooling degree hours. Defaults to 65.
        """

        if self.processed_data.empty:
            data = self.original_data
        else:
            data = self.processed_data

        # Calculate hdh
        data['hdh'] = data[col]
        over_hdh = data.loc[:, col] > hdh_cpoint
        data.loc[over_hdh, 'hdh'] = 0
        data.loc[~over_hdh, 'hdh'] = hdh_cpoint - data.loc[~over_hdh, col]

        # Calculate cdh
        data['cdh'] = data[col]
        under_cdh = data.loc[:, col] < cdh_cpoint
        data.loc[under_cdh, 'cdh'] = 0
        data.loc[~under_cdh, 'cdh'] = data.loc[~under_cdh, col] - cdh_cpoint

        self.processed_data = data

    def add_col_features(self, col=None, degree=None):
        """ Exponentiate columns of dataframe.
        Basically this function squares/cubes a column.
        e.g. df[col^2] = pow(df[col], degree) where degree=2.
        Parameters
        ----------
        col     : list(str)
            Column to exponentiate.
        degree  : list(str)
            Exponentiation degree.
        """

        if not col and not degree:
            return

        else:
            if isinstance(col, list) and isinstance(degree, list):
                if len(col) != len(degree):
                    raise ValueError('col and degree should have equal length.')
                else:
                    if self.processed_data.empty:
                        data = self.original_data
                    else:
                        data = self.processed_data

                    for i in range(len(col)):
                        data.loc[:, col[i] + str(degree[i])] = pow(data.loc[:, col[i]], degree[i]) / pow(10,
                                                                                                         degree[i] - 1)

                    self.processed_data = data
            else:
                raise TypeError('col and degree should be lists.')

    def standardize(self):
        """ Standardize data. """

        if self.processed_data.empty:
            data = self.original_data
        else:
            data = self.processed_data

        scaler = preprocessing.StandardScaler()
        data = pd.DataFrame(scaler.fit_transform(data), columns=data.columns, index=data.index)
        self.processed_data = data

    def normalize(self):
        """ Normalize data. """

        if self.processed_data.empty:
            data = self.original_data
        else:
            data = self.processed_data

        data = pd.DataFrame(preprocessing.normalize(data), columns=data.columns, index=data.index)
        self.processed_data = data

    def add_time_features(self, year=False, month=False, week=False, tod=False, dow=False):
        """ Add time features to dataframe.
        Parameters
        ----------
        year    : bool
            Year.
        month   : bool
            Month.
        week    : bool
            Week.
        tod    : bool
            Time of Day.
        dow    : bool
            Day of Week.
        """

        var_to_expand = []

        if self.processed_data.empty:
            data = self.original_data
        else:
            data = self.processed_data

        if year:
            data["year"] = data.index.year
            var_to_expand.append("year")
        if month:
            data["month"] = data.index.month
            var_to_expand.append("month")
        if week:
            data["week"] = data.index.week
            var_to_expand.append("week")
        if tod:
            data["tod"] = data.index.hour
            var_to_expand.append("tod")
        if dow:
            data["dow"] = data.index.weekday
            var_to_expand.append("dow")

        # One-hot encode the time features
        for var in var_to_expand:
            add_var = pd.get_dummies(data[var], prefix=var, drop_first=True)

            # Add all the columns to the model data
            data = data.join(add_var)

            # Drop the original column that was expanded
            data.drop(columns=[var], inplace=True)

        self.processed_data = data
        return self.processed_data

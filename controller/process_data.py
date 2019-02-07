import datetime
import pandas as pd
import numpy as np

def process_control_df(df, pre_fix=False):
    '''This function takes the dataframe of power values and processes it to add more columns relevant to MPCPy

        Parameters
        ----------
        df: DataFrame
            DataFrame of power consumption values, columns=['FreComp', 'RefComp', 'HVAC1']
        pre_fix : bool
            determines the power limit on freezer compressor

        Returns
        -------
        df: DataFrame
            A processed DataFrame, columns=['FreComp', 'RefComp', 'HVAC1', 'Defrost', 'FreComp_Split',
                'FreHeater_Split', 'FreComp_Split_Norm', 'FreHeater_Split_Norm',
                'RefComp_Norm', 'HVAC1_Norm', 'uHeat', 'uCharge', 'uDischarge']

    '''

    if pre_fix:
        fre_comp_lim = 600
    else:
        fre_comp_lim = 6000

    df.index = pd.to_datetime(df.index.values)
    # Initialize new column
    df['Defrost'] = np.where(df['FreComp'] > fre_comp_lim, True, False)
    # Find when each defrost cycle starts
    times = []
    skip = False
    for time in df.index:
        if (df['FreComp'].loc[time] > fre_comp_lim) and (not skip):
            times.append(time)
            skip = True
        elif (df['FreComp'].loc[time] <= fre_comp_lim):
            skip = False
    for time in times:
        if (time - times[-1] <= datetime.timedelta(minutes=20)):
            df['Defrost'].loc[time:time + datetime.timedelta(minutes=20)] = True

    df['FreComp_Split'] = np.where(df['Defrost'] == True, 0, df['FreComp'])
    df['FreHeater_Split'] = np.where(df['Defrost'] == True, df['FreComp'], 0)

    # Normalize to [0,1]
    for key in ['FreComp_Split', 'FreHeater_Split', 'RefComp', 'HVAC1']:
        key_new = key + '_Norm'
        df[key_new] = df[key] / df[key].max()
        if 'HVAC' in key:
            df[key_new] = np.round(df[key_new] * 2) / 2
        else:
            df[key_new] = np.round(df[key_new])

    df['uHeat'] = 0
    df['uCharge'] = 0
    df['uDischarge'] = 0

    df.index.name = 'Time'
    return df
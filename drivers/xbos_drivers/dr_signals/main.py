import datetime
import json
import logging
import os
from datetime import timedelta

import pandas as pd

from drevent_manager import DREventManager, read_from_json

# CONFIG VARIABLES
FORECAST_PERIOD = 48
FORECAST_FREQUENCY = '15min'
default_pmin = 1
default_pmax = 23

CUSTOM_EVENTS_FILE = 'dr_custom_events.json'
DEFAULT_EVENTS_FILE = 'dr_default_events.json'
NUM_CUSTOM_EVENTS = 0

# Logging
FORMAT = '%(asctime)-15s %(message)s'
logging.basicConfig(format=FORMAT)
logger = logging.getLogger('DR-SERVER')
logger.setLevel(logging.INFO)

# DR events information and state, to keep track of change and trigger new ones
dr_manager = DREventManager(freq=FORECAST_FREQUENCY)


def get_dr_mode(event_type):
    """ Get the DR Mode from the event type.

    Parameters
    ----------
    event_type  : str
        Types include "price-tou", "price-rtp"...

    Returns
    -------
    str
        DR Mode (one of [dr-prices, dr_shed, dr_limit, dr_shift, dr_track])
    """
    if event_type in ['price-tou', 'price-rtp']:
        return 'dr-prices'
    elif event_type in ['dr-limit', "dr-shed", "dr-shift", "dr-track"]:
        return event_type
    else:
        raise ValueError('Event type does not correspond to a valid DR_MODE')


def extract_json(json_result):
    """

    Parameters
    ----------
    json_result : json
        JSON from get_dr_signal()

    Returns
    -------
    list(list), list(list), datetime, datetime
        Price energy list, Price demand list, event start date, event end date
    """
    price_energy_list = []
    for timestamp, price in json_result['customer_energy_charge'].items():
        price_energy_list.append([timestamp, price])

    price_demand_list = []
    for timestamp, price in json_result['customer_demand_charge_tou'].items():
        price_demand_list.append([timestamp, price])

    assert len(price_energy_list) == len(price_demand_list)

    custom_st = datetime.datetime.fromtimestamp(int(price_energy_list[0][0]) / 1000)
    custom_et = datetime.datetime.fromtimestamp(int(price_energy_list[-1][0]) / 1000)

    return price_energy_list, price_demand_list, custom_st, custom_et


# CHECK: CHANGED
def extract_dataframe(df):
    """ Convert price dataframe to list of list.

    Parameters
    ----------
    df  : pd.DataFrame()
        Dataframe from get_default_dr_signal()

    Returns
    -------
    list, list
        List of energy prices, list of demand prices
    """
    a = df.index.tolist()
    b = df['customer_energy_charge'].tolist()
    c = df['customer_demand_charge_tou'].tolist()
    list_energy = [list(x) for x in zip(a, b)]
    list_demand = [list(x) for x in zip(a, c)]

    return list_energy, list_demand


def init_event_scheduler():
    """ Read the type of DR events from the file names.
    TODO: For more robustness, add a function that checks that there's only one default event for each DR mode.
    """
    if os.path.isfile(DEFAULT_EVENTS_FILE):
        default_events = read_from_json(DEFAULT_EVENTS_FILE)
        assert type(default_events) == list

        # Ensure each type has only one default event
        types = [event['type'] for event in default_events]
        assert (len(set(types)) == len(types))

        for event in default_events:
            dr_manager.add_default_dr_events(get_dr_mode(event['type']), event)
    else:
        raise FileNotFoundError(DEFAULT_EVENTS_FILE + ' file not found')


def get_dr_signal(type_dr, start, end):
    """ Get information about a particular dr signal.

    Parameters
    ----------
    type_dr     : str
        Type of dr signal; choose one from ['dr-prices', 'dr_shed', 'dr_limit', 'dr_shift', 'dr_track']
    start       : str
        Start time; format - "YYYY-MM-DDTHH:MM:SS"
    end         : str
        End time; format - "YYYY-MM-DDTHH:MM:SS"

    Returns
    -------
    dict
        Json result

    """
    if (start is not None) and (end is not None):
        time_frame = (start, end)
        result = dr_manager.get_available_events(type_dr, time_frame)
        if not result:
            return None
        return result
    else:
        raise ValueError('start and/or end is None.')


def get_default_dr_signal(type_dr, start, end):
    """ Get information about default dr signal.

    Parameters
    ----------
    type_dr     : str
        Type of dr signal; choose one from ['dr-prices', 'dr_shed', 'dr_limit', 'dr_shift', 'dr_track']
    start       : str
        Start time; format - "YYYY-MM-DDTHH:MM:SS"
    end         : str
        End time; format - "YYYY-MM-DDTHH:MM:SS"

    Returns
    -------
    dict
        Json result

    """
    if (start is not None) and (end is not None):
        time_frame = (start, end)
        result = dr_manager.get_available_default_events(type_dr, time_frame)
        return result
    else:
        raise ValueError('start and/or end is None.')


def update_dr_events():
    """ Read the files describing the DR events and add them internally.
    TODO: For more robustness, add no_overlapping_events() which ensures there are no custom events with
    overlapping time.
    """
    global NUM_CUSTOM_EVENTS

    if os.path.isfile(CUSTOM_EVENTS_FILE):
        custom_events = read_from_json(CUSTOM_EVENTS_FILE)
        assert type(custom_events) == list

        # No new event has been added
        if len(custom_events) <= NUM_CUSTOM_EVENTS:
            print("No new event has been added.")

        # New event(s) has been added
        else:
            for i in range(len(custom_events) - NUM_CUSTOM_EVENTS):
                dr_manager.add_dr_event(get_dr_mode(custom_events[i]['type']), custom_events[i])
            # TODO: Change this later to num_custom_events = len(dr_manager.custom_dr_events)
            NUM_CUSTOM_EVENTS = len(custom_events)
    else:
        raise FileNotFoundError(CUSTOM_EVENTS_FILE + ' file not found')


def get_baseline():
    """ Returns current baseline.

    NOTE: Currently, this function returns a default of 100 kW.

    Returns
    -------
    float
        Baseline (unit = kW)
    """
    # TODO
    return 100


def get_limit(curr_time, end_time):
    """ Gets max power.

    Parameters
    ----------
    curr_time   : datetime
        Current time.
    end_time    : datetime
        Forecast end time.

    Returns
    -------
    list(tuple, float)
        [(start_date, end_date), max_power]
    """
    result = get_dr_signal('dr-limit',
                           curr_time.strftime('%Y-%m-%dT%H:%M:%SZ'),
                           end_time.strftime('%Y-%m-%dT%H:%M:%SZ'))

    if not result:
        return None
    else:
        logger.info('dr-limit custom event')
        pmax = result[0]['data_dr']
        custom_st = datetime.datetime.strptime(result[0]['startdate'], '%Y-%m-%dT%H:%M:%S')
        custom_et = datetime.datetime.strptime(result[0]['enddate'], '%Y-%m-%dT%H:%M:%S')

        return [(custom_st, custom_et), pmax]


def get_shed(curr_time, end_time):
    """ Gets max power.

    Parameters
    ----------
    curr_time   : datetime
        Current time.
    end_time    : datetime
        Forecast end time.

    Returns
    -------
    list(tuple, float)
        [(start_date, end_date), max_power]
    """
    baseline = get_baseline()
    result = get_dr_signal('dr-shed',
                           curr_time.strftime('%Y-%m-%dT%H:%M:%SZ'),
                           end_time.strftime('%Y-%m-%dT%H:%M:%SZ'))

    # Revert to default
    if not result:
        return None
    else:
        logger.info('dr-shed custom event')
        pmax = result[0]['data_dr']
        custom_st = datetime.datetime.strptime(result[0]['startdate'], '%Y-%m-%dT%H:%M:%S')
        custom_et = datetime.datetime.strptime(result[0]['enddate'], '%Y-%m-%dT%H:%M:%S')

        return [(custom_st, custom_et), baseline + pmax]


def get_shift(curr_time, end_time):
    """ Gets max power.

    TODO: Error check to ensure that the power-take and power-relax are not overlapping

    Parameters
    ----------
    curr_time   : datetime
        Current time.
    end_time    : datetime
        Forecast end time.

    Returns
    -------
    list(list(tuple, float))
        [[(start_date, end_date), max_power]...] for power-take and power-relax.
    """
    baseline = get_baseline()
    result = get_dr_signal('dr-shift',
                           curr_time.strftime('%Y-%m-%dT%H:%M:%SZ'),
                           end_time.strftime('%Y-%m-%dT%H:%M:%SZ'))

    # Revert to default
    if not result:
        return None
    else:
        logger.info('dr-shift custom event')
        ptake = result[0]['data_dr']['power-take']
        prelax = result[0]['data_dr']['power-relax']
        ptake_st = datetime.datetime.strptime(result[0]['startdate']['start-date-take'], '%Y-%m-%dT%H:%M:%S')
        ptake_et = datetime.datetime.strptime(result[0]['enddate']['end-date-take'], '%Y-%m-%dT%H:%M:%S')
        prelax_st = datetime.datetime.strptime(result[0]['startdate']['start-date-relax'], '%Y-%m-%dT%H:%M:%S')
        prelax_et = datetime.datetime.strptime(result[0]['enddate']['end-date-relax'], '%Y-%m-%dT%H:%M:%S')

        return [[(ptake_st, ptake_et), baseline + ptake], [(prelax_st, prelax_et), baseline + prelax]]


def get_track(curr_time, end_time):
    """ Gets min and max power.

    Parameters
    ----------
    curr_time   : datetime
        Current time.
    end_time    : datetime
        Forecast end time.

    Returns
    -------
    list(tuple, list(float), float)
        [[(start_date, end_date), [power...], delta]
    """
    result = get_dr_signal('dr-track',
                           curr_time.strftime('%Y-%m-%dT%H:%M:%SZ'),
                           end_time.strftime('%Y-%m-%dT%H:%M:%SZ'))

    # Revert to default
    if not result:
        return None
    else:
        logger.info('dr-track custom event')
        power = result[0]['data_dr']['profile']
        delta = result[0]['data_dr']['delta']
        custom_st = datetime.datetime.strptime(result[0]['startdate'], '%Y-%m-%dT%H:%M:%S')
        custom_et = datetime.datetime.strptime(result[0]['enddate'], '%Y-%m-%dT%H:%M:%S')

        return [(custom_st, custom_et), power, delta]


def get_power(curr_time, end_time):
    """ Get min_power and max_power from all dr power modes.

    Parameters
    ----------
    curr_time   : datetime
        Current time.
    end_time    : datetime
        Forecast end time.

    Returns
    -------
    pd.DataFrame()
        Dataframe containing timestamp, pmin, pmax and dr-mode.
    """
    result = []
    if FORECAST_FREQUENCY == '15min':
        step = timedelta(minutes=15)
    else:
        raise NotImplementedError('Forecast freq = 15min only.')

    limit_pmax = get_limit(curr_time, end_time)
    shed_pmax = get_shed(curr_time, end_time)
    shift_pmax = get_shift(curr_time, end_time)
    track_pmax = get_track(curr_time, end_time)

    if not track_pmax:
        if limit_pmax:
            diff = (limit_pmax[0][1] - limit_pmax[0][0]).total_seconds() / 60
            for date in (limit_pmax[0][0] + timedelta(minutes=n) for n in range(0, int(diff), 15)):
                result.append([date, default_pmin, limit_pmax[1], 'dr-limit'])
        if shed_pmax:
            diff = (shed_pmax[0][1] - shed_pmax[0][0]).total_seconds() / 60
            for date in (shed_pmax[0][0] + timedelta(minutes=n) for n in range(0, int(diff), 15)):
                result.append([date, default_pmin, shed_pmax[1], 'dr-shed'])
        if shift_pmax:
            diff = (shift_pmax[0][0][1] - shift_pmax[0][0][0]).total_seconds() / 60
            for date in (shift_pmax[0][0][0] + timedelta(minutes=n) for n in range(0, int(diff), 15)):
                result.append([date, default_pmin, shift_pmax[0][1], 'dr-shift'])

            diff = (shift_pmax[1][0][1] - shift_pmax[1][0][0]).total_seconds() / 60
            for date in (shift_pmax[1][0][0] + timedelta(minutes=n) for n in range(0, int(diff), 15)):
                result.append([date, default_pmin, shift_pmax[1][1], 'dr-shift'])

    else:  # If there's an event for dr-track, then ignore all other events
        diff = (track_pmax[0][1] - shed_pmax[0][0]).total_seconds() / 60
        pmin = track_pmax[1] - track_pmax[2]
        pmax = track_pmax[1] + track_pmax[2]
        for date in (track_pmax[0][0] + timedelta(minutes=n) for n in range(0, int(diff), 15)):
            result.append([date, pmin, pmax, 'dr-track'])

    power_df = pd.DataFrame(result, columns=['timestamp', 'pmin', 'pmax', 'dr-mode'])
    power_df.set_index('timestamp', inplace=True)
    return power_df


def get_price(curr_time, end_time):
    """ Gets the energy and demand price forecast.

    Parameters
    ----------
    curr_time   : datetime
        Current time.
    end_time    : datetime
        Forecast end time.

    Returns
    -------
    list(list), list(list)
        [[timestamp, energy_price]...], [[timestamp, demand_price]...]
    """
    curr_time_formatted = curr_time.strftime('%Y-%m-%dT%H:%M:%SZ')
    end_time_formatted = end_time.strftime('%Y-%m-%dT%H:%M:%SZ')

    result = get_dr_signal('dr-prices', curr_time_formatted, end_time_formatted)

    # Revert to default event
    if not result:
        logger.info('dr-price default event')
        price_df = get_default_dr_signal('dr-prices', curr_time_formatted, end_time_formatted)
        return price_df['data_dr'][['customer_energy_charge', 'customer_demand_charge_tou']]

    # Custom event
    else:
        logger.info('dr-price custom event')

        # final_energy, final_demand, custom_st, custom_et = extract_json(json_result)
        # custom_st(et) are pandas.Timestamp
        custom_st, custom_et = result[0].index[0], result[0].index[-1]
        price_df = result[0]

        if custom_st > curr_time:
            default_result = get_default_dr_signal('dr-prices',
                                                   curr_time_formatted,
                                                   custom_st.strftime('%Y-%m-%dT%H:%M:%SZ'))
            price_df = pd.concat([default_result['data_dr'], price_df])
        if custom_et < end_time:
            default_result = get_default_dr_signal('dr-prices',
                                                   custom_et.strftime('%Y-%m-%dT%H:%M:%SZ'),
                                                   end_time_formatted)
            price_df = pd.concat([price_df, default_result['data_dr']])

    return price_df[['customer_energy_charge', 'customer_demand_charge_tou']]


if __name__ == '__main__':
    # Add all default events to DREventManager
    init_event_scheduler()

    update_dr_events()

    # CHECK: Time now should be in local time or UTC?
    curr_time = datetime.datetime.now()
    end_time = curr_time + timedelta(hours=FORECAST_PERIOD)

    df_price = get_price(curr_time, end_time)
    df_power = get_power(curr_time, end_time)

    # print('df_price: ', df_price)
    print('df_price: \n', df_price.head())
    print('power: \n', df_power.head())

    df = df_price.join(df_power)
    df['pmin'].fillna(1, inplace=True)
    df['pmax'].fillna(23, inplace=True)
    df['dr-mode'].fillna('default', inplace=True)

    print('df: \n', df.head())

    # df1 = pd.DataFrame(price_energy, columns=['timestamp', 'energy'])
    # df2 = pd.DataFrame(price_demand, columns=['timestamp', 'demand'])
    # df1.set_index('timestamp', inplace=True)
    # df2.set_index('timestamp', inplace=True)
    # df = df1.join(df2, how='outer')
    #
    # df3 = pd.DataFrame(power, columns=['timestamp', 'pmin', 'pmax'])
    # df3.set_index('timestamp', inplace=True)
    # df = df.join(df3, how='outer')
    # df['pmin'].fillna(1, inplace=True)
    # df['pmax'].fillna(23, inplace=True)
    #
    # print('final df in main(): ', df.head())

import yaml
import pandas as pd
import os


# convert original dr data in json format into pandas DataFrame for MPCPy
def dr_json_to_df(dr_json):
    with open(dr_json) as json_file:
        dr_message = yaml.safe_load(json_file)
    dr_data = pd.DataFrame.from_dict(dr_message[0])

    return dr_data


def dr_constraint(dr_json, base_power):
    dr_data = dr_json_to_df(dr_json)
    dr_start = dr_data.loc['start-date', 'data']
    dr_end = dr_data.loc['end-date', 'data']
    # dr_type = dr_data.loc['start-date', 'type']
    # power unit is kW
    power = dr_data.loc['power', 'data']
    dr_limit = base_power + power
    dr_range = pd.date_range(start=dr_start, end=dr_end, freq='5min')
    dr_df = pd.DataFrame(index=dr_range)
    dr_df['dr_limit'] = dr_limit

    return dr_range, dr_limit, dr_df


def create_new_constraint(constraint_df, dr_json, base_power):
    dr_range, dr_limit, dr_df = dr_constraint(dr_json, base_power)
    constraint_df.loc[dr_range, 'Pmax'] = dr_limit

    return constraint_df


dr_file_dir = "../../OpenADR-Virtual-Top-Node/python_api/dr-custom-data/"
dr_file_name = 'dr_limit.json'
dr_file = os.path.join(dr_file_dir, dr_file_name)

constraint_file = '../data/Constraint.csv'
constraint = pd.read_csv(constraint_file, index_col='Time', parse_dates=True)
constraint_df = create_new_constraint(constraint, dr_file, 0)
constraint_df.to_csv('../data/Constraint2.csv')

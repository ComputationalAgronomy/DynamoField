import random
import itertools
import numpy

import csv
import pandas as pd
import dynamo_utils
# numpy.repeat([], 4)

from decimal import Decimal
import field
import boto3
import json




PARTITION_KEY_COLUMN_NAME = field.Field.PARTITION_KEY
SORT_KEY_COLUMN_NAME = field.Field.SORT_KEY


RESERVE_KEYWORDS = [field.Field.PARTITION_KEY, field.Field.SORT_KEY,
                    PARTITION_KEY_COLUMN_NAME, SORT_KEY_COLUMN_NAME, 
                    "row", "column"]


def check_col_names(col_names, df, remove_list=[]):
    if col_names is None:    
        col_names = df.columns.values.tolist()
        remove_list.extend(RESERVE_KEYWORDS)
        for remove in remove_list:
            try:
                col_names.remove(remove)
            except:
                pass
    return col_names




def json_key_type_value(key, type, value):
    json = f"'{key}': {{'{type}': '{value}'}}"
    return json


def json_key_value(key, value):
    json = f"'{key}': '{value}'"
    return json


def create_plot_sort_key(data):
    # sort_key = f"plot_{data['column']:0>2s}{data['row']:0>2s}"
    sort_key = {'info' : f"plot_{data['column']:0>2s}{data['row']:0>2s}"}
    # dynamo_json = dynamo_utils.python_obj_to_dynamo_obj(sort_key)
    # 'trial_id': {'S': 'trial_1A'},
    #     'info': {'S': 'plot_0101'},
    return sort_key 



def create_json_dynamodb(scheme, data):
    json_output = dict()
    for k, v in scheme.items():
        # json_key_type_value(k, v, data[k])
        json_output[k] = json_key_value(k, data[k])
    return json_output 



##############################################################################

def create_partition_key(trial_id):
    partition_key = {field.Field.PARTITION_KEY : f"{trial_id}"}
    return partition_key


def create_sort_key(info):
    sort_key = {field.Field.SORT_KEY : f"{info}"}
    return sort_key


def create_plot_sort_key(prefix, key):
    if not key.startswith(prefix):
        key = f"{prefix}_{key}"
    sort_key = {field.Field.SORT_KEY : key}
    return sort_key



def convert_attribute_dict(col_names, data_s):
    # attr_dict = data_s[col_names].to_dict()
    # attr_dict = {k: v for k, v in data_s.items() if pd.notnull(v)}
    # json_output = dict()
    attr_dict = {k: data_s[k] for k in col_names if pd.notnull(data_s[k])}
        # json_key_type_value(k, v, data[k])
        # json_output[k] = json_key_value(k, data[k])
    # dynamo_json = dynamo_utils.python_obj_to_dynamo_obj(json_output)
    # json_data = json.loads(json.dumps(json_data), parse_float=Decimal)
    return attr_dict 



def reload_dynamo_json(data_dict):
    dynamo_json = json.loads(json.dumps(data_dict), parse_float=Decimal)
    return dynamo_json



def import_field_data_client(client, table_name, dynamo_json_list, dynamo_config={}):
    for dynamo_json in dynamo_json_list:
        dynamo_attribute = dynamo_utils.python_obj_to_dynamo_obj(dynamo_json)
        client.put_item(TableName=table_name, Item=dynamo_attribute, **dynamo_config)



def batch_import_field_data_res(res_table, dynamo_json_list):
    # resource.put_item(Item=dynamo_json_list[0])
    try:
        with res_table.batch_writer() as batch:
            for j in dynamo_json_list:
                batch.put_item(Item=j)
    except Exception as e:
        print(e)


def merge_dicts(partition_key, sort_key, attributes_data):
    try:
        json_data = partition_key | sort_key | attributes_data   # python 3.9 only
    except TypeError:
        json_data = {**partition_key, **sort_key, **attributes_data}
    return json_data




def create_df_column_plot(df):
    rename_mapper = {
        "Plot": "plot",
        "Row": "row",
        "Column": "column",
    }
    df.rename(columns=rename_mapper, inplace=True)
    col_names = df.columns.values.tolist()
    if "plot" in col_names:
        return df
    try:
        index_row = col_names.index("row")
        index_column = col_names.index("column")
    except ValueError as e:
        print(f"Can't parse plot data. {e}")
        raise
    df['plot'] = "plot_" + df['column'].astype(str) + '-' + df['row'].astype(str)
    return df



def parse_df_plot_to_dynamo_json(df, col_names=None):
    sort_key_prefix = "plot"
    col_names = check_col_names(col_names, df, remove_list=[])
    df = create_df_column_plot(df)
    json_list = []    
    df_trials = df.groupby(PARTITION_KEY_COLUMN_NAME)
    for trial_id, df_group in df_trials:
        partition_key = create_partition_key(trial_id)
        for index, dfrow in df_group.reset_index().iterrows():
            sort_key = create_plot_sort_key(sort_key_prefix, dfrow[sort_key_prefix])
            attributes_data = convert_attribute_dict(col_names, dfrow)
            json_data = merge_dicts(partition_key, sort_key, attributes_data)
            json_list.append(json_data)
    dynamo_json_list = [reload_dynamo_json(j) for j in json_list]
    return dynamo_json_list






def parse_df_to_dynamo_json(df, sort_key_prefix, col_names=None):
    json_list = []    
    col_names = check_col_names(col_names, df)
    df_trials = df.groupby(PARTITION_KEY_COLUMN_NAME)
    for trial_id, df_group in df_trials:
        partition_key = create_partition_key(trial_id)
        is_single_row = df_group.shape[0] == 1
        for index, dfrow in df_group.reset_index().iterrows():
            if is_single_row:
                sort_key = create_sort_key(f"{sort_key_prefix}")
            else:
                sort_key = create_sort_key(f"{sort_key_prefix}_{index}")
            attributes_data = convert_attribute_dict(col_names, dfrow)
            json_data = merge_dicts(partition_key, sort_key, attributes_data)
            json_list.append(json_data)
    dynamo_json_list = [reload_dynamo_json(j) for j in json_list]
    return dynamo_json_list









dynamo_config = {'ReturnConsumedCapacity': "INDEXES" }#"Total"}

data_type = "yield"
file_name = f"temp_{data_type}.csv"
df = pd.read_csv(file_name)
df.describe()
df.dtypes
dynamo_json_list = parse_df_plot_to_dynamo_json(df)
batch_import_field_data_res(res_table, dynamo_json_list)



data_type = "trt"
data_type = "yield"


data_type = "trial_meta"
data_type = "trial_contact"
data_type = "trial_management"

for data_type in ["trt", "trial_meta", "trial_contact", "trial_management"]:
    file_name = f"temp_{data_type}.csv"
    df = pd.read_csv(file_name)
    dynamo_json_list = parse_df_to_dynamo_json(df, sort_key_prefix=data_type)
    batch_import_field_data_res(res_table, dynamo_json_list)




dynamo_json_list = parse_df_to_dynamo_json(df, sort_key_prefix="meta")
batch_import_field_data_res(res_table, dynamo_json_list)


import_field_data_client(client, table_name, dynamo_json_list, dynamo_config)



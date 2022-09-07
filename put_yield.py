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


session = boto3.session.Session()
client = session.client('dynamodb', endpoint_url='http://localhost:8000')

client.describe_table(TableName="ft_db")["Table"]["ItemCount"]


trial_id = ["trial_2B", "trial_3C", "trial_4D"]
file_name = f"temp_yield.csv"
nrow = 6
ncol = 4
ntrt  = 6






REQUIRED_COLUMN = {
    "column": "N",
    "row": "N",
    "treatment": "S",
    "yield": "S"
    }

REQUIRED_DATA = ["treatment", "yield"]
REQUIRED_SORT_KEY = {["column", "row"], "plot"}
REQUIRED_SORT_KEY = ["column", "row"]
REQUIRED_PARTITION_KEY = field.Field.PARTITION_KEY





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



def create_json_dict(keys, data):
    # json_output = dict()
    json_output = {k: data[k] for k in keys if pd.notnull(data[k])}
        # json_key_type_value(k, v, data[k])
        # json_output[k] = json_key_value(k, data[k])
    # dynamo_json = dynamo_utils.python_obj_to_dynamo_obj(json_output)
    # json_data = json.loads(json.dumps(json_data), parse_float=Decimal)
    return json_output 







data_type = "yield"
df = pd.read_csv(f"temp_{data_type}.csv")
# df = df.astype(str)
df.describe()
df.dtypes

# df.loc[:,["column","row"]]

print(df)
col_names = df.columns.values.tolist()

# index_column = {col_names.index(k) for k in REQUIRED_COLUMN.keys()}
# index_others = {*range(len(col_names))} - index_column
# _ = [index_others.remove(i) for i in index_column]

data_names = col_names
data_names.remove(REQUIRED_PARTITION_KEY)
_ = [data_names.remove(k) for k in REQUIRED_SORT_KEY]
data_names
dynamo_config = {'ReturnConsumedCapacity': "INDEXES" }#"Total"}

df_trials = df.groupby("trial_id")
for trial_id, df_group in df_trials:
    partition_key = {'trial_id' : f"{trial_id}"}
    for index, dfrow in df_group.iterrows():
        print(dfrow['row'], dfrow['column'])
        sort_key = create_sort_key(dfrow)
        # python_obj_to_dynamo_obj(json_output)
        attributes_data = create_json_dict(data_names, dfrow)
        try:
            json_data = partition_key | sort_key | attributes_data   # python 3.9 only
        except TypeError:
            json_data = {**partition_key, **sort_key, **attributes_data}
        dynamo_json = dynamo_utils.python_obj_to_dynamo_obj(json_data)
        client.put_item(TableName='ft_db', Item = dynamo_json, **dynamo_config)



data_type = "trt"
df = pd.read_csv(f"temp_{data_type}.csv")
# df = df.astype(str)

col_names = df.columns.values.tolist()
data_names = col_names
data_names.remove(REQUIRED_PARTITION_KEY)
data_names


dynamo_config = {'ReturnConsumedCapacity': "INDEXES" }#"Total"}



def parse_df_to_dynamo_json(df, sort_key_prefix, data_names):

    dynamo_json_list = []
    df_trials = df.groupby(field.Field.PARTITION_KEY)
    for trial_id, df_group in df_trials:
        partition_key = create_partition_key(trial_id)

        is_single_row = df_group.shape[0] == 1
        for index, dfrow in df_group.reset_index().iterrows():
            if is_single_row:
                sort_key = create_sort_key(f"{sort_key_prefix}")
            else:
                sort_key = create_sort_key(f"{sort_key_prefix}_{index}")
                
            # sort_key = {'info' : f"{data_type}_{index}"}
            # python_obj_to_dynamo_obj(json_output)
            attributes_data = create_json_dict(data_names, dfrow)
            
            try:
                json_data = partition_key | sort_key | attributes_data   # python 3.9 only
            except TypeError:
                json_data = {**partition_key, **sort_key, **attributes_data}

            dynamo_json = dynamo_utils.python_obj_to_dynamo_obj(json_data)
            dynamo_json_list.append(dynamo_json)


for j in dynamo_json_list:
    client.put_item(TableName='ft_db', 
        Item=j, **dynamo_config)

    # resource.put_item()


data_type = "trial_meta"
df = pd.read_csv(f"temp_{data_type}.csv")
df = df.astype(str)

col_names = df.columns.values.tolist()
data_names = col_names
data_names.remove(REQUIRED_PARTITION_KEY)
data_names

dynamo_config = {'ReturnConsumedCapacity': "INDEXES" }#"Total"}
df_trials = df.groupby("trial_id")

for trial_id, df_group in df_trials:
    partition_key = {'trial_id' : f"{trial_id}"}
    for index, dfrow in df_group.iterrows():
        sort_key = sort_key = {'info' : f"{data_type}"}
        # python_obj_to_dynamo_obj(json_output)
        attributes_data = create_json_dict(data_names, dfrow)
        # partition_key | sort_key | attributes_data  # python 3.9 only
        json_data = {**partition_key, **sort_key, **attributes_data}
        dynamo_json = dynamo_utils.python_obj_to_dynamo_obj(json_data)
        client.put_item(TableName='ft_db', Item = dynamo_json, **dynamo_config)




data_type = "trial_contact"
df = pd.read_csv(f"temp_{data_type}.csv")
# df = df.astype(str)

col_names = df.columns.values.tolist()
data_names = col_names
data_names.remove(REQUIRED_PARTITION_KEY)
data_names

dynamo_config = {'ReturnConsumedCapacity': "INDEXES" }#"Total"}
df_trials = df.groupby("trial_id")

for trial_id, df_group in df_trials:
    partition_key = {'trial_id' : f"{trial_id}"}
    for index, dfrow in df_group.iterrows():
        sort_key = sort_key = {'info' : f"{data_type}"}
        # python_obj_to_dynamo_obj(json_output)
        attributes_data = create_json_dict(data_names, dfrow)
        # partition_key | sort_key | attributes_data  # python 3.9 only
        json_data = {**partition_key, **sort_key, **attributes_data}
        dynamo_json = dynamo_utils.python_obj_to_dynamo_obj(json_data)
        client.put_item(TableName='ft_db', Item = dynamo_json, **dynamo_config)








data_type = "trial_management"
df = pd.read_csv(f"temp_{data_type}.csv")
# df = df.astype(str)

col_names = df.columns.values.tolist()
data_names = col_names
data_names.remove(REQUIRED_PARTITION_KEY)
data_names

dynamo_config = {'ReturnConsumedCapacity': "INDEXES" }#"Total"}
df_trials = df.groupby("trial_id")

for trial_id, df_group in df_trials:
    partition_key = {'trial_id' : f"{trial_id}"}
    for index, dfrow in df_group.reset_index().iterrows():
        sort_key = {'info' : f"{data_type}_{index}"}
        # python_obj_to_dynamo_obj(json_output)
        attributes_data = create_json_dict(data_names, dfrow)
        # partition_key | sort_key | attributes_data  # python 3.9 only
        json_data = {**partition_key, **sort_key, **attributes_data}
        json_data = json.loads(json.dumps(json_data), parse_float=Decimal)
        dynamo_json = dynamo_utils.python_obj_to_dynamo_obj(json_data)
        print(dynamo_json)
        _ = client.put_item(TableName='ft_db', Item = dynamo_json, **dynamo_config)





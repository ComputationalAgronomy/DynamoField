import random
import itertools
import numpy

import csv
import pandas
import dynamo_utils
# numpy.repeat([], 4)





trial_id = ["trial_2B", "trial_3C", "trial_4D"]
file_name = f"temp_yield.csv"
nrow = 6
ncol = 4
ntrt  = 6


simulate_yield_data(trial_id, nrow, ncol, ntrt, file_name)



def simulate_one_trial(trial_id, nrow, ncol, ntrt):
    nrep = int(nrow * ncol / ntrt )
    trt_list =  [ "T"+str(trt) for trt in range(1, ntrt+1, 1) for _ in range(nrep)]
    random.shuffle(trt_list)
    design = itertools.product(range(1, nrow+1, 1), range(1, ncol+1, 1))
    sim_data = [f"{trial_id},{d[0]},{d[1]},{t},{random.uniform(50, 100):.2f},{random.uniform(1, 10):.1f}\n" for d, t in zip(design, trt_list)]
    return(sim_data)


def simulate_yield_data(trial_id, nrow, ncol, ntrt, file_name):
    # list(itertools.product(range(1, 7, 1), range(1, 5, 1)))
    with open(file_name, "w") as f:
        sim_title = "trial_id,row,column,treatment,yield,meta\n"
        f.write(sim_title)
        for trial in trial_id:
            sim_data = simulate_one_trial(trial, nrow, ncol, ntrt)
            f.writelines(sim_data)



REQUIRED_COLUMN = {
    "column": "N",
    "row": "N",
    "treatment": "S",
    "yield": "S"
    }

REQUIRED_DATA = ["treatment", "yield"]
REQUIRED_SORT_KEY = {["column", "row"], "plot"}
REQUIRED_SORT_KEY = ["column", "row"]
REQUIRED_PRIMARY_KEY = "trial_id"





def json_key_type_value(key, type, value):
    json = f"'{key}': {{'{type}': '{value}'}}"
    return(json)


def json_key_value(key, value):
    json = f"'{key}': '{value}'"
    return(json)


def create_sort_key(data):
    sort_key = f"plot_{data['column']:0>2s}{data['row']:0>2s}"
    sort_key = {'info' : f"plot_{data['column']:0>2s}{data['row']:0>2s}"}
    # dynamo_json = dynamo_utils.python_obj_to_dynamo_obj(sort_key)
    # 'trial_id': {'S': 'trial_1A'},
    #     'info': {'S': 'plot_0101'},
    return(sort_key)



def create_json_dynamodb(scheme, data):
    json_output = dict()
    for k, v in scheme.items():
        # json_key_type_value(k, v, data[k])
        json_output[k] = json_key_value(k, data[k])
    return(json_output)


def create_json_dict(keys, data):
    # json_output = dict()
    json_output = {k:data[k] for k in keys}
        # json_key_type_value(k, v, data[k])
        # json_output[k] = json_key_value(k, data[k])
    # dynamo_json = dynamo_utils.python_obj_to_dynamo_obj(json_output)
    return(json_output)




from decimal import Decimal
Decimal(2.4)



df = pandas.read_csv(file_name)
df = df.astype(str)
df.describe()
df.dtypes

# df.loc[:,["column","row"]]

print(df)
col_names = df.columns.values.tolist()

# index_column = {col_names.index(k) for k in REQUIRED_COLUMN.keys()}
# index_others = {*range(len(col_names))} - index_column
# _ = [index_others.remove(i) for i in index_column]

data_names = col_names
data_names.remove(REQUIRED_PRIMARY_KEY)
_ = [data_names.remove(k) for k in REQUIRED_SORT_KEY]
data_names
dynamo_config = {'ReturnConsumedCapacity': "INDEXES" }#"Total"}

df_trials = df.groupby("trial_id")
for trial_id, df_group in df_trials:
    primary_key = {'trial_id' : f"{trial_id}"}
    for index, dfrow in df_group.iterrows():
        print(dfrow['row'], dfrow['column'])
        sort_key = create_sort_key(dfrow)
        # python_obj_to_dynamo_obj(json_output)
        attributes_data = create_json_dict(data_names, dfrow)
        # primary_key | sort_key | attributes_data  # python 3.9 only
        json_data = {**primary_key, **sort_key, **attributes_data}
        dynamo_json = dynamo_utils.python_obj_to_dynamo_obj(json_data)
        client.put_item(TableName='ft_db', Item = dynamo_json, **dynamo_config)






data_type = "trt"
df = pandas.read_csv(f"temp_{data_type}.csv")
df = df.astype(str)

col_names = df.columns.values.tolist()
data_names = col_names
data_names.remove(REQUIRED_PRIMARY_KEY)
data_names

dynamo_config = {'ReturnConsumedCapacity': "INDEXES" }#"Total"}
df_trials = df.groupby("trial_id")

for trial_id, df_group in df_trials:
    primary_key = {'trial_id' : f"{trial_id}"}
    for index, dfrow in df_group.iterrows():
        sort_key = sort_key = {'info' : f"{data_type}_{dfrow['trt_number']}"}
        # python_obj_to_dynamo_obj(json_output)
        attributes_data = create_json_dict(data_names, dfrow)
        # primary_key | sort_key | attributes_data  # python 3.9 only
        json_data = {**primary_key, **sort_key, **attributes_data}
        dynamo_json = dynamo_utils.python_obj_to_dynamo_obj(json_data)
        client.put_item(TableName='ft_db', Item = dynamo_json, **dynamo_config)




data_type = "trialmeta"
df = pandas.read_csv(f"temp_{data_type}.csv")
df = df.astype(str)

col_names = df.columns.values.tolist()
data_names = col_names
data_names.remove(REQUIRED_PRIMARY_KEY)
data_names

dynamo_config = {'ReturnConsumedCapacity': "INDEXES" }#"Total"}
df_trials = df.groupby("trial_id")

for trial_id, df_group in df_trials:
    primary_key = {'trial_id' : f"{trial_id}"}
    for index, dfrow in df_group.iterrows():
        sort_key = sort_key = {'info' : f"{data_type}"}
        # python_obj_to_dynamo_obj(json_output)
        attributes_data = create_json_dict(data_names, dfrow)
        # primary_key | sort_key | attributes_data  # python 3.9 only
        json_data = {**primary_key, **sort_key, **attributes_data}
        dynamo_json = dynamo_utils.python_obj_to_dynamo_obj(json_data)
        client.put_item(TableName='ft_db', Item = dynamo_json, **dynamo_config)








with open(file_name, "r") as f:
    # data = csv.reader(f, delimiter=',', quotechar='"')
    # data[0]
    # for l in data:
    #     print(l)
    col_names = f.readline().strip().split(",")
    print(col_names)
    for l in f.readlines():
        plot = l.strip().split(",")
        [plot[i] for i in index_column]
        print(l.strip())
            


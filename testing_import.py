import boto3
# import field
import importlib
import pandas as pd
from field import importer
from field import field_table

import dynamodb_init
importlib.reload(field_table)
importlib.reload(importer)

data_import = importer.DataImporter(file_name, "meta")


dynamo_json_list = data_import.parse_df_to_dynamo_json()


table_name = "ft_db"
dynamodb_res = dynamodb_init.init_dynamodb_resources()
field_trial = field_table.FieldTable(dynamodb_res, table_name)

field_trial.batch_import_field_data_res(dynamo_json_list)


dynamo_config = {'ReturnConsumedCapacity': "INDEXES" }#"Total"}

data_type = "yield"
file_name = f"temp_{data_type}.csv"
df = pd.read_csv(file_name)
df.describe()
df.dtypes

data_import = importer.DataImporter(file_name, data_type="plot")
dynamo_json_list = data_import.parse_df_plot_to_dynamo_json()

field_trial.batch_import_field_data_res(dynamo_json_list)



data_type = "trt"
data_type = "yield"


data_type = "trial_meta"
data_type = "trial_contact"
data_type = "trial_management"

field_trial = field_table.FieldTable(dynamodb_res, table_name)

for data_type in ["trt", "trial_meta", "trial_contact", "trial_management"]:
    data_import = importer.DataImporter(file_name, data_type)
    dynamo_json_list = data_import.parse_df_to_dynamo_json()
    field_trial.batch_import_field_data_res(dynamo_json_list)

    # file_name = f"temp_{data_type}.csv"
    # df = pd.read_csv(file_name)
    # dynamo_json_list = parse_df_to_dynamo_json(df, sort_key_prefix=data_type)
    # batch_import_field_data_res(res_table, dynamo_json_list)




dynamo_json_list = parse_df_to_dynamo_json(df, sort_key_prefix="meta")
batch_import_field_data_res(res_table, dynamo_json_list)


import_field_data_client(client, table_name, dynamo_json_list, dynamo_config)



###################################
field_trial = field_table.FieldTable(dynamodb_res, table_name)


trial_id = ["trial_3C", "trial_2B"]
trial_id = "trial_3C"
trial_id = "trial_2B"


field_trial.get_by_trial_id(trial_id)
field_trial.get_by_trial_id(trial_id=["trial_3C", "trial_2B"], sort_key="plot_0202")
field_trial.get_by_trial_id(trial_id, sort_key="aoeu")


list_sort_key = field_trial.list_all_sort_keys(trial_id)



df_plots = field_trial.get_all_plots(trial_id)
convert_float = ["yield", "meta"]
for col in convert_float:
    df_plots[col] = df_plots[col].astype("float") 

df_plots.describe()
df_plots.info()

df_plots.groupby("treatment").mean()


df_trt = field_trial.get_all_treatments(trial_id)



pd.merge(df_plots, df_trt, how="inner", on=["trial_id", "treatment"])

list_sort_key = field_trial.list_all_sort_keys(trial_id)
field_trial.list_all_sort_keys(trial_id, prune_common=True)
field_trial.get_all_non_standard_info(trial_id)



sort_key = "trial_meta"
sort_key = "trial_management"
field_trial.get_by_sort_key(sort_key, type="begins")

sort_key = "trial_contact"
field_trial.get_by_sort_key(sort_key)


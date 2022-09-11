import csv
import itertools
import json
import random
from decimal import Decimal

import boto3
import numpy
import pandas as pd

import dynamo_utils
import field
import json_utils

# numpy.repeat([], 4)


class DataImporter:


    PARTITION_KEY_COLUMN_NAME = field.FieldTable.PARTITION_KEY
    SORT_KEY_COLUMN_NAME = field.FieldTable.SORT_KEY


    RESERVE_KEYWORDS = [field.FieldTable.PARTITION_KEY, field.FieldTable.SORT_KEY,
                        PARTITION_KEY_COLUMN_NAME, SORT_KEY_COLUMN_NAME, 
                        "row", "column"]

    RENAME_MAPPER = {
        "Plot": "plot",
        "Row": "row",
        "Column": "column",
    }




    @staticmethod
    def create_plot_sort_key(prefix, key):
        if not key.startswith(prefix):
            key = f"{prefix}_{key}"
        sort_key = {field.FieldTable.SORT_KEY : key}
        return sort_key


    @staticmethod
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



    @staticmethod
    def merge_dicts(partition_key, sort_key, attributes_data):
        try:
            json_data = partition_key | sort_key | attributes_data   # python 3.9 only
        except TypeError:
            json_data = {**partition_key, **sort_key, **attributes_data}
        return json_data






    def __init__(self, file_name, data_type):
        # self.res_table = res_table
        self.df = pd.read_csv(file_name)
        self.data_type = data_type



    
    def check_col_names(self, col_names, remove_list=[]):
        if col_names is None:    
            col_names = self.df.columns.values.tolist()
            remove_list.extend(DataImporter.RESERVE_KEYWORDS)
            for remove in remove_list:
                try:
                    col_names.remove(remove)
                except:
                    pass
        return col_names




    def create_df_plot_column(self):

        self.df.rename(columns=DataImporter.RENAME_MAPPER, inplace=True)
        col_names = df.columns.values.tolist()
        if not "plot" in col_names:
            try:
                index_row = col_names.index("row")
                index_column = col_names.index("column")
            except ValueError as e:
                print(f"Can't parse plot data. {e}")
                raise
            self.df['plot'] = "plot_" + \
                self.df['column'].astype(str) + '-' + \
                self.df['row'].astype(str)

    


    def complicated_sort_key_creation(is_single_row, sort_key_prefix, index, dfrow):
        '''
        Overly complicated way to create sort key.
        Redo this part later.
        '''
        if sort_key_prefix == "plot":
            sort_key = DataImporter.create_plot_sort_key(sort_key_prefix, dfrow[sort_key_prefix])
        elif is_single_row:
            sort_key = field.FieldTable.create_sort_key(f"{sort_key_prefix}")
        else:
            sort_key = field.FieldTable.create_sort_key(f"{sort_key_prefix}_{index}")
        return sort_key
    

    def parse_df_to_dynamo_json(self, sort_key_prefix, col_names=None):
        json_list = []
        col_names = self.check_col_names(col_names, remove_list=[])
        df_trials = self.df.groupby(field.FieldTable.PARTITION_KEY)
        for trial_id, df_group in df_trials:
            partition_key = field.FieldTable.create_partition_key(trial_id)
            is_single_row = df_group.shape[0] == 1
            for index, dfrow in df_group.reset_index().iterrows():
                sort_key = DataImporter.complicated_sort_key_creation(
                    is_single_row, sort_key_prefix, index, dfrow)
                attributes_data = DataImporter.convert_attribute_dict(
                    col_names, dfrow)
                json_data = DataImporter.merge_dicts(
                    partition_key, sort_key, attributes_data)
                json_list.append(json_data)
        dynamo_json_list = [
            json_utils.reload_dynamo_json(j) for j in json_list]
        return dynamo_json_list




    def parse_df_plot_to_dynamo_json(self, col_names=None):
        sort_key_prefix = "plot"
        dynamo_json_list = self.parse_df_to_dynamo_json(sort_key_prefix, col_names)
        return dynamo_json_list


    def parse_df_plot_to_dynamo_json(self, col_names=None):
        sort_key_prefix = "trt"
        dynamo_json_list = self.parse_df_to_dynamo_json(sort_key_prefix, col_names)
        return dynamo_json_list





    def import_field_data_client(client, table_name, dynamo_json_list, dynamo_config={}):
        for dynamo_json in dynamo_json_list:
            dynamo_attribute = dynamo_utils.python_obj_to_dynamo_obj(dynamo_json)
            client.put_item(TableName=table_name, Item=dynamo_attribute, **dynamo_config)



    def batch_import_field_data_res(self, dynamo_json_list):
        # resource.put_item(Item=dynamo_json_list[0])
        try:
            with self.res_table.batch_writer() as batch:
                for j in dynamo_json_list:
                    batch.put_item(Item=j)
        except Exception as e:
            print(e)







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



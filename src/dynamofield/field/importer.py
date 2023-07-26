import csv
import itertools
import json
import random
from decimal import Decimal

import boto3
import numpy
import pandas as pd

from dynamofield.db import db_keys
from dynamofield.field import field_table
from dynamofield.utils import dict_utils, dynamo_utils, json_utils


class DataImporter:

    PARTITION_KEY_COLUMN_NAME = field_table.FieldTable.PARTITION_KEY_NAME
    SORT_KEY_COLUMN_NAME = field_table.FieldTable.SORT_KEY_NAME

    RESERVE_KEYWORDS = [field_table.FieldTable.PARTITION_KEY_NAME,
                        field_table.FieldTable.SORT_KEY_NAME,
                        PARTITION_KEY_COLUMN_NAME, SORT_KEY_COLUMN_NAME,
                        "row", "column"]

    RENAME_MAPPER = {
        "Plot": "plot",
        "Row": "row",
        "Column": "column",
    }

    def __init__(self, input, data_type, import_column=[]):
        # self.res_table = res_table
        if isinstance(input, pd.DataFrame):
            self.df = input
        else:
            self.df = pd.read_csv(input)
        self.data_type = data_type  # sort_key
        self.import_column = import_column
        self.dynamo_json_list = []
        self.partition_key_collection = set()
        if len(self.import_column) == 0:
            self.import_column = self.df.columns.values.tolist()
        if self.data_type == "plot":
            self.create_df_plot_column()


    def check_col_names(self, remove_list=[]):
        remove_list.extend(DataImporter.RESERVE_KEYWORDS)
        for remove in remove_list:
            try:
                self.import_column.remove(remove)
            except ValueError:
                pass

    def check_dup_key_prefix(self, key):
        if not key.startswith(self.data_type):
            key = f"{self.data_type}_{key}"
        return key

    def create_df_plot_column(self):
        self.df.rename(columns=DataImporter.RENAME_MAPPER, inplace=True)
        col_names = self.df.columns.values.tolist()
        if "plot" not in col_names:
            try:
                index_row = col_names.index("row")
                index_column = col_names.index("column")
            except ValueError as e:
                print(f"Can't parse plot data. {e}")
                raise
            self.df['plot'] = "plot_" + \
                self.df['column'].astype(str) + '-' + \
                self.df['row'].astype(str)

    def convert_attribute_dict(self, data_s):
        # attr_dict = data_s[col_names].to_dict()
        # attr_dict = {k: v for k, v in data_s.items() if pd.notnull(v)}
        # json_output = dict()
        attr_dict = {k: data_s[k]
                     for k in self.import_column if pd.notnull(data_s[k])}
        # json_key_type_value(k, v, data[k])
        # json_output[k] = json_key_value(k, data[k])
        # dynamo_json = dynamo_utils.python_obj_to_dynamo_obj(json_output)
        # json_data = json.loads(json.dumps(json_data), parse_float=Decimal)
        return attr_dict

    def sort_key_creation(self, index, dfrow):
        if self.data_type == "plot":
            key = self.check_dup_key_prefix(dfrow[self.data_type])
        # elif is_single_row:
        #     key = self.data_type
        else:
            key = f"{self.data_type}_{index}"
        sort_key = field_table.FieldTable.create_sort_key(key)
        return sort_key



    def create_offset(self, df_trials, append, field_trial):
        offset = {k: 0 for k in df_trials.groups.keys()}
        if append:
            try:
                offset = field_trial.find_offset(self.data_type)
            except AttributeError:
                pass
            except KeyError:
                pass
        return offset

    def parse_df_to_dynamo_json(self, append=False,
                                db_table: field_table.FieldTable = None):
        json_list = []
        self.check_col_names(remove_list=[])
        df_trials = self.df.groupby(field_table.FieldTable.PARTITION_KEY_NAME)
        offset = self.create_offset(df_trials, append, db_table)
        self.partition_key_collection = set()
        for trial_id, df_group in df_trials:
            partition_key = field_table.FieldTable.create_partition_key(trial_id)
            self.partition_key_collection.add(trial_id)
            # is_single_row = df_group.shape[0] == 1
            for index_raw, dfrow in df_group.reset_index().iterrows():
                index = index_raw + offset[trial_id]
                sort_key = self.sort_key_creation(index, dfrow)
                attributes_data = self.convert_attribute_dict(dfrow)
                json_data = dict_utils.merge_dicts(
                    partition_key, sort_key, attributes_data)
                json_list.append(json_data)
        self.dynamo_json_list = [
            json_utils.reload_dynamo_json(j) for j in json_list]
        # return dynamo_json_list, partition_key_collection




    def parse_df_plot_to_dynamo_json(self):
        sort_key_prefix = "plot"
        self.create_df_plot_column()
        self.parse_df_to_dynamo_json()
        # return dynamo_json_list


    def parse_df_trt_to_dynamo_json(self):
        sort_key_prefix = "trt"
        # self.create_df_trt_column()
        self.parse_df_to_dynamo_json()
        # return dynamo_json_list

    # def parse_df_plot_to_dynamo_json(self, col_names=None):
    #     sort_key_prefix = "trt"
    #     dynamo_json_list = self.parse_df_to_dynamo_json(sort_key_prefix, col_names)
    #     return dynamo_json_list

#     # reduce(lambda x: x.split("_")[1], xx)

# current_data_split.aggregate({"info": lambda x : x.split("_")})

# current_data_split.aggregate({"info": lambda x : str(x)})

# current_data_split.get_group(trial_id).apply(lambda x: [1,2], index=["info"], axis=0)
# current_data_split.get_group(trial_id)["info"].apply(lambda x: x.split(), axis=1)

# current_data_split["info"].apply(lambda x : find_offset(x))
# xx = current_data_split["info"].aggregate(lambda x : find_offset(x))

# current_data_split.info.aggregate(lambda x : [s.rsplit("_")[1] for s in x])


# current_data_split.get_group(trial_id)["info"].apply(lambda x: x.split("_")[1])



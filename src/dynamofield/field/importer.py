import csv
import itertools
import json
import random
from decimal import Decimal

import boto3
import numpy
import pandas as pd

from dynamofield.utils import dynamo_utils
from dynamofield.utils import json_utils
from dynamofield.utils import dict_utils

# numpy.repeat([], 4)
from dynamofield.field import field_table


class DataImporter:

    PARTITION_KEY_COLUMN_NAME = field_table.FieldTable.PARTITION_KEY
    SORT_KEY_COLUMN_NAME = field_table.FieldTable.SORT_KEY

    RESERVE_KEYWORDS = [field_table.FieldTable.PARTITION_KEY,
                        field_table.FieldTable.SORT_KEY,
                        PARTITION_KEY_COLUMN_NAME, SORT_KEY_COLUMN_NAME,
                        "row", "column"]

    RENAME_MAPPER = {
        "Plot": "plot",
        "Row": "row",
        "Column": "column",
    }

    def __init__(self, file_name, data_type, import_column=None):
        # self.res_table = res_table
        self.df = pd.read_csv(file_name)
        self.data_type = data_type  # sort_key
        self.import_column = import_column
        if self.data_type == "plot":
            self.create_df_plot_column()

    def check_col_names(self, remove_list=[]):
        if self.import_column is None:
            self.import_column = self.df.columns.values.tolist()
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

    def complicated_sort_key_creation(self, is_single_row, index, dfrow):
        '''
        Overly complicated way to create sort key.
        Redo this part later.
        '''
        if self.data_type == "plot":
            key = self.check_dup_key_prefix(dfrow[self.data_type])
        elif is_single_row:
            key = self.data_type
        else:
            key = f"{self.data_type}_{index}"
        sort_key = field_table.create_sort_key(key)
        return sort_key

    def parse_df_to_dynamo_json(self):
        json_list = []
        self.check_col_names(remove_list=[])
        df_trials = self.df.groupby(field_table.FieldTable.PARTITION_KEY)

        for trial_id, df_group in df_trials:
            partition_key = field_table.create_partition_key(trial_id)
            is_single_row = df_group.shape[0] == 1
            for index, dfrow in df_group.reset_index().iterrows():
                sort_key = self.complicated_sort_key_creation(
                    is_single_row, index, dfrow)
                attributes_data = self.convert_attribute_dict(dfrow)
                json_data = dict_utils.merge_dicts(
                    partition_key, sort_key, attributes_data)
                json_list.append(json_data)

        dynamo_json_list = [
            json_utils.reload_dynamo_json(j) for j in json_list]
        return dynamo_json_list

    def parse_df_plot_to_dynamo_json(self):
        sort_key_prefix = "plot"
        self.create_df_plot_column()
        dynamo_json_list = self.parse_df_to_dynamo_json()
        return dynamo_json_list

    def parse_df_trt_to_dynamo_json(self):
        sort_key_prefix = "trt"
        # self.create_df_trt_column()
        dynamo_json_list = self.parse_df_to_dynamo_json()
        return dynamo_json_list

    # def parse_df_plot_to_dynamo_json(self, col_names=None):
    #     sort_key_prefix = "trt"
    #     dynamo_json_list = self.parse_df_to_dynamo_json(sort_key_prefix, col_names)
    #     return dynamo_json_list

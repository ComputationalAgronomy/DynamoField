import json
import logging
from decimal import Decimal

import boto3
import pandas as pd
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError

from dynamofield.db import db_keys
from dynamofield.utils import dict_utils, dynamo_utils, json_utils

# from io import BytesIO
# import os
# from pprint import pprint
# import requests
# from zipfile import ZipFile
# from question import Question


# def create_partition_key(trial_id):
#     partition_key = {FieldTable.PARTITION_KEY: f"{trial_id}"}
#     return partition_key


# def create_sort_key(info):
#     sort_key = {FieldTable.SORT_KEY: f"{info}"}
#     return sort_key


logger = logging.getLogger(__name__)


class FieldTable:
    """Encapsulates an Amazon DynamoDB table of field trial data."""
    PARTITION_KEY_NAME = "field_trial_id"
    SORT_KEY_NAME = "data_type"
    PARTITION_KEY = Key(PARTITION_KEY_NAME)
    SORT_KEY = Key(SORT_KEY_NAME)
    TRIAL_ID_LIST_PARTITION_KEY = "__private_list_all_id__"

    def __init__(self, dyn_resource, table_name):
        """
        :param dyn_resource: A Boto3 DynamoDB resource.
        """
        self.dyn_resource = dyn_resource
        self.res_table = self.dyn_resource.Table(table_name)

    @staticmethod
    def create_partition_key(trial_id):
        partition_key = db_keys.create_db_key(FieldTable.PARTITION_KEY_NAME, trial_id)
        return partition_key

    @staticmethod
    def create_sort_key(info):
        sort_key = db_keys.create_db_key(FieldTable.SORT_KEY_NAME, info)
        return sort_key

    @staticmethod
    def parse_sort_key_condition(value, exact):
        sort_key_exprs = db_keys.parse_key_condition(
            FieldTable.SORT_KEY, value, exact)
        return sort_key_exprs

    @staticmethod
    def template_query_table(table, keywords):
        try:
            response = table.query(**keywords)
        except ClientError as err:
            logger.error(
                "Couldn't query field trial. Here's why: %s: %s",
                err.response['Error']['Code'], err.response['Error']['Message'])
            raise
        else:
            return response  # ['Items']
        pass

    @staticmethod
    def template_scan_table(table, scan_kwargs):
        """
        Scans all data and deal with page limits via LastEvaluatedKey
        :return: The list
        """
        results = []
        try:
            done = False
            start_key = None
            while not done:
                if start_key:
                    scan_kwargs['ExclusiveStartKey'] = start_key
                response = table.scan(**scan_kwargs)
                results.extend(response.get('Items', []))
                start_key = response.get('LastEvaluatedKey', None)
                done = start_key is None
        except ClientError as err:
            logger.error(
                "Couldn't scan for trial. Here's why: %s: %s",
                err.response['Error']['Code'], err.response['Error']['Message'])
            raise
        return results

    def template_query(self, keywords):
        return FieldTable.template_query_table(self.res_table, keywords)

    def template_scan(self, scan_kwargs):
        return FieldTable.template_scan_table(self.res_table, scan_kwargs)





    def convert_partition_key_collection_dynamo_json(self, partition_key_collection):
        json_list = []
        partition_key = FieldTable.create_partition_key(FieldTable.TRIAL_ID_LIST_PARTITION_KEY)
        for t in partition_key_collection:
            sort_key = self.create_sort_key(t)
            json_data = dict_utils.merge_dicts(partition_key, sort_key, {})
            json_list.append(json_data)
        dynamo_json = [json_utils.reload_dynamo_json(j) for j in json_list]
        return dynamo_json



    def import_batch_field_data_res(self, data_importer):
        # resource.put_item(Item=dynamo_json_list[0])
        if len(data_importer.dynamo_json_list) == 0 or len(data_importer.partition_key_collection) == 0:
            print("Incomplete importer. Nothing to import\n")
            return 0
        id_json = self.convert_partition_key_collection_dynamo_json(data_importer.partition_key_collection)
        try:
            with self.res_table.batch_writer() as batch:
                for j in data_importer.dynamo_json_list:
                    batch.put_item(Item=j)
                for j in id_json:
                    batch.put_item(Item=j)
        except Exception as e:
            print(e)
            print(data_importer.dynamo_json_list)
            print(id_json)
        return len(data_importer.dynamo_json_list)


    def list_all_sort_keys(self, trial_id, prune_common=False):
        key = FieldTable.PARTITION_KEY.eq(trial_id)
        keywords = {"KeyConditionExpression": key,
                    "ProjectionExpression": FieldTable.SORT_KEY_NAME}
        response = self.res_table.query(**keywords)
        sort_key_list = []

        for item in response['Items']:
            sort_key_list.append(item.get("info"))
        if prune_common:
            other_sort_keys = [i for i in sort_key_list if not i.startswith(
                'plot_') | i.startswith('trt_')]
            return other_sort_keys

        return sort_key_list


    def get_item_count(self):
        self.res_table.reload()
        return self.res_table.item_count


    def get_all_non_standard_info(self, trial_id):
        list_sort_keys = self.list_all_sort_keys(trial_id, prune_common=True)

        partn_key = FieldTable.PARTITION_KEY.eq(trial_id)
        other_info_dict = {}
        for sort_key in list_sort_keys:
            primary_keys = partn_key & FieldTable.SORT_KEY.eq(sort_key)
            keywords = {"KeyConditionExpression": primary_keys}
            response = self.res_table.query(**keywords)
            other_info_dict[sort_key] = response["Items"]
        # for item in response['Items']:
        #     sort_key_list.append(item.get("info"))

        return other_info_dict


    def get_all_trial_id(self):
        response = self.query_by_single_trial_id(FieldTable.TRIAL_ID_LIST_PARTITION_KEY)
        all_ids = [t["info"] for t in response]
        return all_ids


    def query_df_all_plots(self, trial_ids):
        """
        High level function. Retrieve all plots information for a list of trial_ids
        """
        results = self.query_by_trial_ids(trial_ids, sort_keys="plot_", exact=False)
        df = json_utils.result_list_to_df(results)
        return df


    def query_df_all_treatments(self, trial_ids) -> pd.DataFrame:
        """
        High level function. Retrieve all treatment information for a list of trial_ids
        """
        results = self.query_by_trial_ids(trial_ids, sort_keys="trt_", exact=False)
        df = json_utils.result_list_to_df(results)
        return df


    def query_df_plot_treatment(self, trial_ids):
        df_plots = self.query_df_all_plots(trial_ids)
        df_trt = self.query_df_all_treatments(trial_ids)
        df_merged = pd.merge(df_plots, df_trt, how="inner", on=["trial_id", "treatment"])
        return df_merged


    def query_df_by_two_sort_keys(self, trial_ids, info_1, info_2, merged_by):
        df = {}
        results = self.query_by_trial_ids(trial_ids, sort_keys=f"{info_1}_", exact=False)
        df[info_1] = json_utils.result_list_to_df(results)
        results = self.query_by_trial_ids(trial_ids, sort_keys=f"{info_2}_", exact=False)
        df[info_2] = json_utils.result_list_to_df(results)
        df_merged = pd.merge(df[info_1], df[info_2], how="inner", on=["trial_id", merged_by])
        return df_merged


    def query_by_single_trial_id(self, trial_id, sort_keys=[], exact=False):
        """
        :param trial_id: Trial ID
        :return: All info relate to the given trial ID.
        """
        sort_keys = db_keys.check_sort_keys(sort_keys)
        parti_key_exprs = FieldTable.PARTITION_KEY.eq(trial_id)
        # if not isinstance(sort_keys, list) and len(sort_keys) > 0:
        #     sort_keys = [sort_keys]
        # if sort_keys is not None:
        #     sort_key_exprs = FieldTable.parse_sort_key_condition(sort_keys, exact)
        #     keys_exprs = keys_exprs & sort_key_exprs
        results = list()
        for s in sort_keys:
            sort_key_exprs = FieldTable.parse_sort_key_condition(s, exact)
            keys_exprs = parti_key_exprs & sort_key_exprs
            keywords = {"KeyConditionExpression": keys_exprs}
            response = self.template_query(keywords)
            results.extend(response['Items'])
        if len(sort_keys) == 0:
            keywords = {"KeyConditionExpression": parti_key_exprs}
            response = self.template_query(keywords)
            results.extend(response['Items'])
        return results


    def query_by_trial_ids(self, trial_ids, sort_keys=[], exact=False):
        if not isinstance(trial_ids, list):
            trial_ids = [trial_ids]
        sort_keys = db_keys.check_sort_keys(sort_keys)
        results = list()
        for trial_id in trial_ids:
            temp = self.query_by_single_trial_id(trial_id, sort_keys=sort_keys, exact=exact)
            results.extend(temp)
        # df = json_utils.result_list_to_df(results)
        return results


    def get_by_sort_key(self, sort_key, exact=False):
        sort_key_exprs = self.parse_sort_key_condition(sort_key, exact)
        scan_kwargs = {
            'FilterExpression': sort_key_exprs
        }
        results = self.template_scan(scan_kwargs)
        df = json_utils.result_list_to_df(results)

        return df

    # def parse_sort_key_expression(sort_key, exact):
    #     if exact:
    #             sort_keys = Key(FieldTable.SORT_KEY).eq(sort_key)
    #     else:
    #         sort_keys = Key(FieldTable.SORT_KEY).begins_with(sort_key)
    #     return(sort_keys)



    def find_offset(self, data_type):
        # try:
        current_data = self.get_by_sort_key(data_type)
        current_data_split = current_data.groupby(FieldTable.PARTITION_KEY_NAME)
        offset = current_data_split["info"].aggregate(lambda x : db_keys.find_offset_sort_key_list(x))
        # except NameError:
        #     offest =
        return offset



    @DeprecationWarning
    def __import_field_data_client(client, table_name, dynamo_json_list, dynamo_config={}):
        for dynamo_json in dynamo_json_list:
            dynamo_attribute = dynamo_utils.python_obj_to_dynamo_obj(
                dynamo_json)
            client.put_item(TableName=table_name,
                            Item=dynamo_attribute, **dynamo_config)

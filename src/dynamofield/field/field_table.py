import json
import logging
from decimal import Decimal

import boto3
import pandas as pd
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError

from dynamofield.utils import dynamo_utils
from dynamofield.utils import json_utils

# from io import BytesIO
# import os
# from pprint import pprint
# import requests
# from zipfile import ZipFile
# from question import Question


def create_partition_key(trial_id):
    partition_key = {FieldTable.PARTITION_KEY: f"{trial_id}"}
    return partition_key


def create_sort_key(info):
    sort_key = {FieldTable.SORT_KEY: f"{info}"}
    return sort_key


logger = logging.getLogger(__name__)


class FieldTable:
    """Encapsulates an Amazon DynamoDB table of field trial data."""
    PARTITION_KEY = "trial_id"
    SORT_KEY = "info"

    def __init__(self, dyn_resource, table_name):
        """
        :param dyn_resource: A Boto3 DynamoDB resource.
        """
        self.dyn_resource = dyn_resource
        self.res_table = self.dyn_resource.Table(table_name)


    def import_field_data_client(client, table_name, dynamo_json_list, dynamo_config={}):
        for dynamo_json in dynamo_json_list:
            dynamo_attribute = dynamo_utils.python_obj_to_dynamo_obj(
                dynamo_json)
            client.put_item(TableName=table_name,
                            Item=dynamo_attribute, **dynamo_config)


    def batch_import_field_data_res(self, dynamo_json_list):
        # resource.put_item(Item=dynamo_json_list[0])
        try:
            with self.res_table.batch_writer() as batch:
                for j in dynamo_json_list:
                    batch.put_item(Item=j)
        except Exception as e:
            print(e)


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


    def list_all_sort_keys(self, trial_id, prune_common=False):
        key = Key(FieldTable.PARTITION_KEY).eq(trial_id)
        keywords = {"KeyConditionExpression": key,
                    "ProjectionExpression": FieldTable.SORT_KEY}
        response = self.res_table.query(**keywords)
        sort_key_list = []

        for item in response['Items']:
            sort_key_list.append(item.get("info"))
        if prune_common:
            other_sort_keys = [i for i in sort_key_list if not i.startswith(
                'plot_') | i.startswith('trt_')]
            return other_sort_keys

        return sort_key_list

    def get_all_non_standard_info(self, trial_id):
        list_sort_keys = self.list_all_sort_keys(trial_id, prune_common=True)

        partn_key = Key(FieldTable.PARTITION_KEY).eq(trial_id)
        other_info_dict = {}
        for sort_key in list_sort_keys:
            primary_keys = partn_key & Key(FieldTable.SORT_KEY).eq(sort_key)
            keywords = {"KeyConditionExpression": primary_keys}
            response = self.res_table.query(**keywords)
            other_info_dict[sort_key] = response["Items"]
        # for item in response['Items']:
        #     sort_key_list.append(item.get("info"))

        return other_info_dict


    def get_all_plots(self, trial_ids):
        """
        Scans all plots and return data
        :return: The list of plots
        """
        if not isinstance(trial_ids, list):
            trial_ids = [trial_ids]
        results = list()
        sort_key = Key(FieldTable.SORT_KEY).begins_with("plot_")
        for trial_id in trial_ids:
            partn_key = Key(FieldTable.PARTITION_KEY).eq(trial_id)
            scan_kwargs = {
                'FilterExpression': partn_key & sort_key
            }
            results.extend(self.template_scan(scan_kwargs))
        df = json_utils.result_list_to_df(results)
        return df

    def get_all_treatments(self, trial_id):
        """
        Scans all plots and return data
        :return: The list of plots
        """
        partn_key = Key(FieldTable.PARTITION_KEY).eq(trial_id)
        sort_key = Key(FieldTable.SORT_KEY).begins_with("trt_")
        scan_kwargs = {
            # "KeyConditionExpression": Keys,
            # 'ProjectionExpression': "#yr, title, info.rating",
            'FilterExpression': partn_key & sort_key
        }
        results = self.template_scan(scan_kwargs)
        df = json_utils.result_list_to_df(results)
        return df

    def get_by_sort_key(self, sort_key, exact=False):
        
        if exact:
            sort_keys = Key(FieldTable.SORT_KEY).eq(sort_key)
        else:
            sort_keys = Key(FieldTable.SORT_KEY).begins_with(sort_key)
        scan_kwargs = {
            'FilterExpression': sort_keys
        }
        results = self.template_scan(scan_kwargs)
        df = json_utils.result_list_to_df(results)

        return df

    def get_by_trial_id(self, trial_id, sort_key=None):
        """
        :param trial_id: Trial ID
        :return: All info relate to the given trial ID.
        """
        keys = Key(FieldTable.PARTITION_KEY).eq(trial_id)
        if sort_key is not None:
            keys = keys & Key(FieldTable.SORT_KEY).eq(sort_key)
        keywords = {"KeyConditionExpression": keys}

        response = self.template_query(keywords)
        return response['Items']

    def find_offset(self, data_type):
        # try:
        current_data = self.get_by_sort_key(data_type)
        current_data_split = current_data.groupby(FieldTable.PARTITION_KEY)
        offset = current_data_split["info"].aggregate(lambda x : FieldTable._find_offset_sort_key_list(x))
        # except NameError:
        #     offest = 
        return offset

    def _find_offset_sort_key_list(x):
        index = [int(s.rsplit("_")[1]) for s in x]
        offset = max(index)
        return(offset)


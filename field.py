import json
import logging
from decimal import Decimal

import boto3
import pandas as pd
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError

import json_utils

# from io import BytesIO
# import os
# from pprint import pprint
# import requests
# from zipfile import ZipFile
# from question import Question



logger = logging.getLogger(__name__)


class Field:
    """Encapsulates an Amazon DynamoDB table of field trial data."""
    PARTITION_KEY = "trial_id"
    SORT_KEY = "info"

    def __init__(self, dyn_resource, table_name):
        """
        :param dyn_resource: A Boto3 DynamoDB resource.
        """
        self.dyn_resource = dyn_resource
        self.res_table = self.dyn_resource.Table(table_name)

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
            return response#['Items']
        pass

    @staticmethod
    def template_scan_table(table, scan_kwargs):
        """
        Scans all plots and return data
        :return: The list of plots
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
        return Field.template_query_table(self.res_table, keywords)


    def template_scan(self, scan_kwargs):
        return Field.template_scan_table(self.res_table, scan_kwargs)


    def list_all_sort_keys(self, trial_id, prune_common=False):
        
        Keys = Key(Field.PARTITION_KEY).eq(trial_id)
        keywords = {"KeyConditionExpression": Keys, 
                    "ProjectionExpression": Field.SORT_KEY}
        response = self.res_table.query(**keywords)
        sort_key_list = []
        for item in response['Items']:
            sort_key_list.append(item.get("info"))
        if prune_common:
            other_sort_keys = [i for i in sort_key_list if not i.startswith('plot_') | i.startswith('trt_')]    
            return other_sort_keys

        return sort_key_list
    

    
    def get_all_non_standard_info(self, trial_id):
        list_sort_keys = self.list_all_sort_keys(trial_id, prune_common=True)
        
        Keys = Key(Field.PARTITION_KEY).eq(trial_id)
        other_info_dict = {}
        for sort_key in list_sort_keys:
            primary_keys = Keys & Key(Field.SORT_KEY).eq(sort_key)
            keywords = {"KeyConditionExpression": primary_keys}
            response = self.res_table.query(**keywords)
            other_info_dict[sort_key] = response["Items"]
        # for item in response['Items']:
        #     sort_key_list.append(item.get("info"))
        
        return other_info_dict


    def get_all_plots(self, trial_id):
        """
        Scans all plots and return data
        :return: The list of plots
        """
        Keys = Key(Field.PARTITION_KEY).eq(trial_id)
        scan_kwargs = {
            #"KeyConditionExpression": Keys, 
            'FilterExpression': Keys & Key(Field.SORT_KEY).begins_with("plot_")
            # 'ProjectionExpression': "#yr, title, info.rating",
        }
        results = self.template_scan(scan_kwargs)
        df = json_utils.result_list_to_df(results)
        return df



    def get_all_treatments(self, trial_id):
        """
        Scans all plots and return data
        :return: The list of plots
        """
        Keys = Key(Field.PARTITION_KEY).eq(trial_id)
        scan_kwargs = {
            #"KeyConditionExpression": Keys, 
            'FilterExpression': Keys & Key(Field.SORT_KEY).begins_with("trt_")}
            # 'ProjectionExpression': "#yr, title, info.rating",
        results = self.template_scan(scan_kwargs)
        df = json_utils.result_list_to_df(results)
        return df
        


    def get_by_sort_key(self, sort_key, type="eq"):
        
        Keys = Key(Field.SORT_KEY).eq(sort_key)
        if type == "begins":
            Keys = Key(Field.SORT_KEY).begins_with(sort_key)
        elif type != "eq":
            logging.warning(f"Invalid Key type: {type}")
        scan_kwargs = {
            'FilterExpression': Keys
        }
        results = self.template_scan(scan_kwargs)
        df = json_utils.result_list_to_df(results)
        
        return df


    def get_by_trial_id(self, trial_id, sort_key=None):
            """
            :param trial_id: Trial ID
            :return: All info relate to the given trial ID.
            """
            Keys = Key(Field.PARTITION_KEY).eq(trial_id)
            if sort_key is not None:
                Keys = Keys & Key(Field.SORT_KEY).eq(sort_key)
            keywords = {"KeyConditionExpression": Keys}
            
            response = self.template_query(keywords)
            return response['Items']

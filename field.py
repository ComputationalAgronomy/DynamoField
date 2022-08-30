import boto3
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError
import json
import logging


from decimal import Decimal

import pandas as pd

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
        self.table = self.dyn_resource.Table('ft_db')


    def query_template(self, keywords):
        try:
            response = self.table.query(**keywords)
        except ClientError as err:
            logger.error(
                "Couldn't query field trial. Here's why: %s: %s",
                err.response['Error']['Code'], err.response['Error']['Message'])
            raise
        else:
            return response#['Items']
        pass


    def scan_template(self, scan_kwargs):
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
                response = self.table.scan(**scan_kwargs)
                results.extend(response.get('Items', []))
                start_key = response.get('LastEvaluatedKey', None)
                done = start_key is None
        except ClientError as err:
            logger.error(
                "Couldn't scan for trial. Here's why: %s: %s",
                err.response['Error']['Code'], err.response['Error']['Message'])
            raise
        return results




    def query_trial(self, trial_id, sort_key=None):
        """
        :param trial_id: Trial ID
        :return: All info relate to the given trial ID.
        """
        Keys = Key(Field.PARTITION_KEY).eq(trial_id)
        if sort_key is not None:
            Keys = Keys & Key(Field.SORT_KEY).eq(sort_key)
        keywords = {"KeyConditionExpression": Keys}
        
        response = self.query_template(keywords)
        return response['Items']



    def get_all_sort_keys(self, trial_id):
        
        Keys = Key(Field.PARTITION_KEY).eq(trial_id)
        keywords = {"KeyConditionExpression": Keys, 
                    "ProjectionExpression": Field.SORT_KEY}
        response = self.table.query(**keywords)
        sort_key_list = []
        for item in response['Items']:
            sort_key_list.append(item.get("info"))
        
        return sort_key_list


    def get_all_non_standard_info(self, trial_id):
        list_sort_keys = self.get_all_sort_keys(trial_id)
        other_sort_keys = [i for i in list_sort_keys if not i.startswith('plot_') | i.startswith('trt_')]

        Keys = Key(Field.PARTITION_KEY).eq(trial_id)
        other_info_dict = {}
        for sort_key in other_sort_keys:
            primary_keys = Keys & Key(Field.SORT_KEY).eq(sort_key)
            keywords = {"KeyConditionExpression": primary_keys}
            response = self.table.query(**keywords)
            other_info_dict[sort_key] = response["Items"]
        # for item in response['Items']:
        #     sort_key_list.append(item.get("info"))
        
        return other_info_dict

    def scan_plots(self, trial_id):
        """
        Scans all plots and return data
        :return: The list of plots
        """
        Keys = Key(Field.PARTITION_KEY).eq(trial_id)
        scan_kwargs = {
            #"KeyConditionExpression": Keys, 
            'FilterExpression': Keys & Key(Field.SORT_KEY).begins_with("plot_")}
            # 'ProjectionExpression': "#yr, title, info.rating",
        results = self.scan_template(scan_kwargs)
        df_list = [pd.DataFrame.from_dict(r, orient='index') for r in results]
        df = pd.concat(df_list, axis=1).transpose()

        return df



    def scan_treatments(self, trial_id):
        """
        Scans all plots and return data
        :return: The list of plots
        """
        Keys = Key(Field.PARTITION_KEY).eq(trial_id)
        scan_kwargs = {
            #"KeyConditionExpression": Keys, 
            'FilterExpression': Keys & Key(Field.SORT_KEY).begins_with("trt_")}
            # 'ProjectionExpression': "#yr, title, info.rating",
        results = self.scan_template(scan_kwargs)
        df = pd.read_json(json.dumps(results))
        return df
        df_list = [pd.DataFrame.from_dict(r, orient='index') for r in results]
        df = pd.concat(df_list, axis=1).transpose()

        return df





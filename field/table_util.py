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

def delete_all_items(client):
    # KeyConditionExpression='trial_id = :trial_id AND begins_with( info, :info)',
    # response = client.query(
    #     TableName='ft_db',
    #     FilterExpression='begins_with(trial_id, :trial_id)',
    #     # KeyConditionExpression='trial_id = :trial_id',
    #     FilterExpression='begins_with ( info , :info )',
    #     ExpressionAttributeValues={
    #         # ':trial_id': {'S': 'trial_3C'},
    #         ':info': {'S': 'plot_01'},
    #     },
    #     ProjectionExpression='trial_id, info',
    # )
    # print(response['Items'])
    response = client.scan(
        TableName='ft_db',
        FilterExpression='begins_with ( trial_id , :trial_id )',
        # FilterExpression='info = :info',
        ExpressionAttributeValues={
            ':trial_id': {'S': 'trial_'},
            # ':info': {'S': 'trialmeta'},
        },
        ProjectionExpression='trial_id, info',
        ReturnConsumedCapacity="Total",
    )
    print(response['Items'])
    for k in response['Items']:
        client.delete_item(TableName="ft_db", Key=k)


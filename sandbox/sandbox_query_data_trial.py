import boto3
import json

from boto3.dynamodb.conditions import Key, Attr
from botocore.exceptions import ClientError


session = boto3.session.Session()
client = session.client('dynamodb', endpoint_url='http://localhost:8000')


table_name = "ft_db"

def get_item_count(client, table_name):
    count = client.describe_table(TableName="table_name")["Table"]["ItemCount"]
    return count



response = client.query(
    TableName='ft_db',
    KeyConditionExpression='trial_id = :trial_id',
    ExpressionAttributeValues={
        ':trial_id': {'S': 'trial_2B'},
        # ':info': {'S': 'plot'}
    }
)
print(response['Items'])
response['Items'][1]



response = client.query(
    TableName='ft_db',
    KeyConditionExpression='trial_id = :trial_id AND begins_with ( info , :info )',
    ExpressionAttributeValues={
        ':trial_id': {'S': 'trial_3C'},
        ':info': {'S': 'plot'}
    },
    ReturnConsumedCapacity="Indexes"
)
print(response['Items'])




def query_trial(client, table_name, partition_key, sort_key_prefix="p"):
    response = client.query(
        TableName=table_name,
        KeyConditionExpression='trial_id = :trial_id AND begins_with ( info , :info )',
        ExpressionAttributeValues={
            ':trial_id': {'S': partition_key},
            ':info': {'S': sort_key_prefix},
        },
        # ProjectionExpression='#trt,#y',
        # ExpressionAttributeNames={
        #     "#trt":"treatment",
        #     "#y":"yield"
        # },
        PageSize=5,
        ReturnConsumedCapacity="Total"
    )
    print(response['Items'])


query_trial(client, table_name, "trial_2B", "'")










response = client.scan(
    TableName='ft_db',
    FilterExpression='begins_with ( info , :info )',
    # FilterExpression='info = :info',
    ExpressionAttributeValues={
        ':info': {'S': 'trt_2'},
        # ':info': {'S': 'trialmeta'},
    },
    ReturnConsumedCapacity="Total"
)
print(response['Items'])




response = client.scan(
    TableName='ft_db',
    FilterExpression=' yield <> :yield ',
    # FilterExpression='info = :info',
    ExpressionAttributeValues={
        ':yield': {'S': ''},
        # ':info': {'S': 'trialmeta'},
    },
    ReturnConsumedCapacity="Total"
)
print(response['Items'])




response = client.query(
    TableName='ft_db',
    KeyConditionExpression='trial_id = :trial_id',
    ExpressionAttributeValues={
        ':trial_id': {'S': 'trial_2B'},
    },
    ProjectionExpression='info',
    ReturnConsumedCapacity="Total"
)
print(response['Items'])



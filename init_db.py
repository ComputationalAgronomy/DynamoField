import boto3
import json

# client_aws = boto3.client('dynamodb')
# response = client_aws.describe_endpoints()
# response = client_aws.list_tables()

session = boto3.session.Session()
client = session.client('dynamodb', 
    endpoint_url='http://localhost:8000')
#     aws_access_key_id='temp',
#     aws_secret_access_key='temp',
# )

response = client.list_tables()

def init_ft_table(client):
    response = client.create_table(
        AttributeDefinitions=[
            {
                'AttributeName': 'trial_id',
                'AttributeType': 'S'
            },
            {
                'AttributeName': 'info',
                'AttributeType': 'S'
            }
        ],
        TableName='ft_db',
        KeySchema=[
            {
                'AttributeName': 'trial_id',
                'KeyType': 'HASH'
            },
            {
                'AttributeName': 'info',
                'KeyType': 'RANGE'
            }
        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': 10,
            'WriteCapacityUnits': 10
        },
    )    


client.describe_table(TableName='ft_db')


dynamodb = session.resource('dynamodb', endpoint_url='http://localhost:8000')
table = dynamodb.Table('ft_db')
table.item_count
table.key_schema






client.put_item(
    TableName='ft_db',
    Item = {
        'trial_id': {'S': 'trial_1A'},
        'info': {'S': 'plot_0101'},
        'row': {'N': '1'},
        'column': {'N': '1'},
        'yield': {'N': '1105'},
    }
)

client.put_item(
    TableName='ft_db',
    Item = {
        {'trial_id': {'S': 'trial_1A'}},
        {'info': {'S': 'plot_0101'}},
        {'row': {'N': '1'},
        'column': {'N': '1'},
        'yield': {'N': '1105'}},
    }
)



client.get_item(TableName='ft_db',
    Key={'trial_id': {'S': 'trial_3C'},
        'info': {'S': 'plot_0101'}
    }
)



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
        ':trial_id': {'S': 'trial_2B'},
        ':info': {'S': 'plot'}
    },
    ReturnConsumedCapacity="Indexes"
)
print(response['Items'])



response = client.query(
    TableName='ft_db',
    KeyConditionExpression='trial_id = :trial_id AND begins_with ( info , :info )',
    ExpressionAttributeValues={
        ':trial_id': {'S': 'trial_2B'},
        ':info': {'S': 'plot_'},
    },
    ProjectionExpression='#trt,#y',
    ExpressionAttributeNames={
        "#trt":"treatment",
        "#y":"yield"
    },
    ReturnConsumedCapacity="Total"
)
print(response['Items'])




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




# from boto3.dynamodb.types import TypeDeserializer

# def ddb_deserialize(r, type_deserializer = TypeDeserializer()):
#     return type_deserializer.deserialize({"M": r})

# def lambda_handler(event, context):
#     new_images = [ ddb_deserialize(r["dynamodb"]["NewImage"]) for r in event['Records'] ]
#     print('Converted records', json.dumps(new_images, indent=2))

import dynamo_utils
json_string = {"row": 2, "column": 2, "yield": 310}
x=dynamo_utils.python_obj_to_dynamo_obj(json_string)
# dynamo_utils.dynamo_obj_to_python_obj(x)
# json_obj = json.dumps(json_string)

dynamo_json_string = {"row": {"N":"2"}, "column": {"N":"2"}, "yield": {"N":"123"}}
dynamo_utils.dynamo_obj_to_python_obj(dynamo_json_string)


json_string = '{"row": 2, "column": 2, "yield": 310}'
json_obj = json.loads(json_string)

dynamodb = session.resource('dynamodb', endpoint_url='http://localhost:8000')
table = dynamodb.Table('ft_db')

table.put_item(Item={
    'trial_id': 'trial_1A',
    'info': 'plot_0202',
    **json_obj
    }
)

jj = table.get_item(
    Key={'trial_id': 'trial_1A',
        'info': 'plot_0202'
    }
)
jj["Item"]["yield"]

response = table.scan(
Select="ALL_ATTRIBUTES",
)
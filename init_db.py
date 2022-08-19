import boto3

client_aws = boto3.client('dynamodb')
response = client_aws.describe_endpoints()
response = client_aws.list_tables()

session = boto3.session.Session()

client = session.client('dynamodb', 
    endpoint_url='http://localhost:8000',
    aws_access_key_id='temp',
    aws_secret_access_key='temp',
)

response = client.describe_endpoints()
response = client.list_tables()


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

client.put_item(
    TableName='ft_db',
    Item = {
        'trial_id': {'S': 'trial_1A'},
        'info': {'S': 'plot_0101'},
        'row': {'N': '1'},
        'column': {'N': '1'},
        'yield': {'N': '105'},
    }
)

client.get_item(TableName='ft_db',
    Key={'trial_id': {'S': 'trial_1A'},
        'info': {'S': 'plot_0101'}
    }
)

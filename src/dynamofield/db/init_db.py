import botocore 

def init_db_table(client, table_name):
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
        TableName=table_name,
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

def remove_table(client, table_name):
    try:
        client.delete_table(TableName=table_name)
    except botocore.errorfactory.ClientError as e:
        print(f"Table does NOT exist: {table_name}. Error: {e}")


# client.describe_table(TableName='ft_db')

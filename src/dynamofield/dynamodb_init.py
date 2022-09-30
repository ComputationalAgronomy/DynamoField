import boto3 
import botocore


def init_dynamodb_client(endpoint_url='http://localhost:8000'):
    session = boto3.session.Session()
    client = session.client('dynamodb', endpoint_url=endpoint_url)
    # client.describe_table(TableName=table_name)["Table"]["ItemCount"]
    # isinstance(client, botocore.client.BaseClient)
    return client

def init_dynamodb_resources(endpoint_url='http://localhost:8000'):
    session = boto3.session.Session()
    dynamodb_res = session.resource('dynamodb', endpoint_url=endpoint_url)
    # isinstance(dynamodb_res, boto3.resources.base.ServiceResource)
    return dynamodb_res

def init_dynamodb_resources_table(endpoint_url='http://localhost:8000', table_name=None):
    dynamodb_res = init_dynamodb_resources(endpoint_url)
    res_table = dynamodb_res.Table(table_name)
    # res_table.item_count
    # isinstance(res_table, boto3.resources.base.ServiceResource)
    return res_table

import boto3 
import botocore

table_name = "ft_db"


session = boto3.session.Session()

client = session.client('dynamodb', endpoint_url='http://localhost:8000')
client.describe_table(TableName=table_name)["Table"]["ItemCount"]
isinstance(client, botocore.client.BaseClient)


dynamodb_res = session.resource('dynamodb', endpoint_url='http://localhost:8000')
res_table = dynamodb_res.Table(table_name)
res_table.item_count
isinstance(res_table, boto3.resources.base.ServiceResource)
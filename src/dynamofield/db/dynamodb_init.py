import boto3
import botocore.exceptions

class DynamodbServer:

    def __init__(self, endpoint_url='http://localhost:8000'):
        self.session = boto3.session.Session()
        self.endpoint_url = endpoint_url

    def init_dynamodb_client(self):
        client = self.session.client('dynamodb', endpoint_url=self.endpoint_url)
        # client.describe_table(TableName=table_name)["Table"]["ItemCount"]
        # isinstance(client, botocore.client.BaseClient)
        try:
            test = client.list_tables()
        except botocore.exceptions.EndpointConnectionError as e:
            print(f"Invalid DynamoDB connection or server: {e}")
        return client

    def init_dynamodb_resources(self):
        dynamodb_res = self.session.resource('dynamodb', endpoint_url=self.endpoint_url)
        # isinstance(dynamodb_res, boto3.resources.base.ServiceResource)
        try:
            test = list(dynamodb_res.tables.all())
            # test = next(dynamodb_res.tables.pages())
        except botocore.exceptions.EndpointConnectionError as e:
            print(f"Invalid DynamoDB connection or server: {e}")
            print(f"Attempt to restart the local server")
            return "RETRY"
        return dynamodb_res

    def init_dynamodb_resources_table(self, table_name):
        dynamodb_res = self.init_dynamodb_resources()
        res_table = dynamodb_res.Table(table_name)
        # res_table.item_count
        # isinstance(res_table, boto3.resources.base.ServiceResource)
        return res_table


 

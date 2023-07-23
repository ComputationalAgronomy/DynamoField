import boto3
import botocore
import botocore.exceptions

from dynamofield.db import db_client


class DynamodbServer:

    def __init__(self, endpoint_url='http://localhost:8000'):
        self.session = boto3.session.Session()
        if len(self.session.available_profiles) == 0 and self.session.get_credentials() is None:
            self.session = boto3.session.Session(
                aws_access_key_id="local",
                aws_secret_access_key="local",
                region_name="local",
            )
        self.dynamodb_res = None
        self.is_online = False
        self.update_endpoint(endpoint_url)

    def update_endpoint(self, endpoint):
        # any([p in endpoint for p in ["http://", "https://"]])
        is_protocol = any([endpoint.startswith(p) for p in ["http://", "https://"]])
        if not is_protocol:
            endpoint = f"http://{endpoint}"
        self.endpoint_url = endpoint
        self.init_dynamodb_resources()

    def create_new_table(self, tablename):
        client = self.session.client('dynamodb', endpoint_url=self.endpoint_url)
        response = db_client.add_db_table(client, tablename)
        return response

    def delete_table(self, tablename):
        client = self.session.client('dynamodb', endpoint_url=self.endpoint_url)
        response = db_client.remove_table(client, tablename)
        return response

    def delete_all_data_type(self, tablename, sort_key):
        client = self.session.client('dynamodb', endpoint_url=self.endpoint_url)
        response = db_client.delete_all_items_sort_key(client, tablename, sort_key)
        return response

    def init_dynamodb_client(self):
        client = self.session.client('dynamodb', endpoint_url=self.endpoint_url)
        # client.describe_table(TableName=table_name)["Table"]["ItemCount"]
        # isinstance(client, botocore.client.BaseClient)
        try:
            _ = client.list_tables()
        except botocore.exceptions.EndpointConnectionError as e:
            print(f"Invalid DynamoDB connection or server: {e}")
        return client

    def list_tables(self):
        return list(self.dynamodb_res.tables.all())

    def is_dynamodb_online(self):
        self.is_online = False
        try:
            _ = self.list_tables()
            self.is_online = True
            # test = next(dynamodb_res.tables.pages())
        except botocore.exceptions.EndpointConnectionError as e:
            print(f"Invalid DynamoDB connection or server: {e}")
        except botocore.exceptions.ClientError as e:
            print(f"Invalid endpoint or credential: {e}")


    def init_dynamodb_resources(self):
        self.dynamodb_res = self.session.resource('dynamodb', endpoint_url=self.endpoint_url)
        self.is_dynamodb_online()
        # is_online = self.is_online
        # if is_online:
        #     print("res:online")
        # elif not is_online:
        print(f"==DEBUG== Resource online: {self.is_online}")
        # isinstance(dynamodb_res, boto3.resources.base.ServiceResource)

        return self.is_online

    def init_dynamodb_resources_table(self, table_name):
        res_table = self.dynamodb_res.Table(table_name)
        # res_table.item_count
        # isinstance(res_table, boto3.resources.base.ServiceResource)
        return res_table

    def is_table_exist(self, table_name):
        res_table = self.dynamodb_res.Table(table_name)
        try:
            status = res_table.table_status
            status = True
        except botocore.exceptions.EndpointConnectionError as e:
            print(f"Invalid DynamoDB connection or server: {e}")
            # print(f"Attempt to restart the local server")
            status = False
        except botocore.exceptions.ClientError as e:
            print(f"Invalid Table name or other errors: {e}")
            status = False
        return status


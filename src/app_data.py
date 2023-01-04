
import boto3

from dynamofield.db import dynamodb_init, init_db, key_utils, table_utils
from dynamofield.field import field_table


def init_dynamodb(endpoint_url):
    print("init db")
    # client = dynamodb_init.init_dynamodb_client()
    # table_utils.delete_all_items(client, table_name)
    dynamodb_server = dynamodb_init.DynamodbServer(endpoint_url=endpoint_url)
    # client = dynamodb_server.init_dynamodb_client()
    # dynamodb_server.init_dynamodb_resources()
    # print("srv:", dynamodb_server.is_online, dynamodb_server.dynamodb_res)
    return dynamodb_server

def init_field_trial(dynamodb_server, table_name = "ft_db"):
    # dynamodb_res = 
    # table_name = "ft_db"
    dynamodb_res = dynamodb_server.dynamodb_res
    # print("FT:", dynamodb_server.is_online, dynamodb_server.dynamodb_res)
    # if dynamodb_res == "RETRY":
    #     init_db.start_dynamodb_server()
    #     dynamodb_res = dynamodb_server.init_dynamodb_resources()
    field_trial = field_table.FieldTable(dynamodb_res, table_name)
    return field_trial

endpoint_url_local = 'http://localhost:8000'
table_name_default = "ft_db"
dynamodb_server = init_dynamodb(endpoint_url=endpoint_url_local)
# print("ZZ:", dynamodb_server.is_online, dynamodb_server.dynamodb_res)
field_trial = init_field_trial(dynamodb_server, table_name = table_name_default)


def start_db():
    try:
        field_trial = init_field_trial()
    except:
        print("Database offline")


def update_item_count():
    try:
        item_counts = field_trial.get_item_count()
        output = f"Total item count: {item_counts}"
    except:
        output = f"Database offline."
    return output
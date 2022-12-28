
import boto3

from dynamofield.db import dynamodb_init, init_db, key_utils, table_utils
from dynamofield.field import field_table


def init_field_trial():

    table_name = "ft_db"
    # client = dynamodb_init.init_dynamodb_client()
    # table_utils.delete_all_items(client, table_name)
    dynamodb_server = dynamodb_init.DynamodbServer()
    # client = dynamodb_server.init_dynamodb_client()
    dynamodb_res = dynamodb_server.init_dynamodb_resources()
    field_trial = field_table.FieldTable(dynamodb_res, table_name)
    return field_trial


field_trial = init_field_trial()


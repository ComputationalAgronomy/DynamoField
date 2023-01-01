
import boto3

from dynamofield.db import dynamodb_init, init_db, key_utils, table_utils
from dynamofield.field import field_table


def init_field_trial():
    print("init db")
    table_name = "ft_db"
    # client = dynamodb_init.init_dynamodb_client()
    # table_utils.delete_all_items(client, table_name)
    dynamodb_server = dynamodb_init.DynamodbServer()
    # client = dynamodb_server.init_dynamodb_client()
    dynamodb_res = dynamodb_server.init_dynamodb_resources()
    if dynamodb_res == "RETRY":
        init_db.start_dynamodb_server()
        dynamodb_res = dynamodb_server.init_dynamodb_resources()
    field_trial = field_table.FieldTable(dynamodb_res, table_name)
    return field_trial


field_trial = init_field_trial()

def update_item_count():
    item_counts = field_trial.get_item_count()
    output = f"Total item count: {item_counts}"
    return output
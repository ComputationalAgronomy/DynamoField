# import field
import importlib
import os

import boto3
import numpy as np
import pandas as pd
import pytest

from dynamofield.db import client_internal, db_client, dynamodb_server
from dynamofield.field import field_table, importer

# importlib.reload(field_table)
# importlib.reload(importer)
# importlib.reload(init_db)

@pytest.fixture
def field_trial():
    table_name = "ft_db"
    dynamodb = dynamodb_server.DynamodbServer()
    field_trial = field_table.FieldTable(dynamodb.dynamodb_res, table_name)
    return field_trial



# @pytest.mark.first
def test_creation():
    table_name = "ft_db"
    dynamodb = dynamodb_server.DynamodbServer()
    # dynamodb_res = dynamodb_server.init_dynamodb_resources()
    client = dynamodb.init_dynamodb_client()
    init_num_table = len(client.list_tables()["TableNames"])
    if init_num_table == 0:
        init_num_table = 1
    db_client.remove_table(client, table_name)
    del_length = len(client.list_tables()["TableNames"])
    assert del_length == init_num_table - 1

    db_client.add_db_table(client, table_name)
    final_length = len(client.list_tables()["TableNames"])
    assert final_length == del_length + 1

    table_desc = client.describe_table(TableName = table_name)
    expected = {'Table': {
        'AttributeDefinitions':
                [{'AttributeName': 'trial_id', 'AttributeType': 'S'},
                    {'AttributeName': 'info', 'AttributeType': 'S'}],
                'TableName': 'ft_db',
                'KeySchema': [{'AttributeName': 'trial_id', 'KeyType': 'HASH'},
                    {'AttributeName': 'info', 'KeyType': 'RANGE'}],
                'TableStatus': 'ACTIVE',
                'ItemCount': 0
                }}
    assert expected["Table"].items() <= table_desc["Table"].items()



def test_import(field_trial: field_table.FieldTable):

    TEST_DATA_DIR = "./tests/test_data"
    hidden_key = 3
    expected_length = {
        "trt": 18,
        "contact": 4,
        "meta": 3,
        "management": 12,
        "plot": 72
    }
    total = np.cumsum(list(expected_length.values())) + hidden_key
    expected_total = dict(zip(expected_length.keys(), total))

    # for data_type in ["trt", "trial_meta", "trial_contact", "trial_management"]:
    count = field_trial.get_item_count()
    assert count == 0
    for data_type in expected_length.keys():
        print(data_type)
        file_name = os.path.join(TEST_DATA_DIR, f"test_{data_type}.csv")
        data_importer = importer.DataImporter(file_name, data_type)
        data_importer.parse_df_to_dynamo_json(append=True, db_table=field_trial)
        assert len(data_importer.dynamo_json_list) == expected_length[data_type]
        field_trial.import_batch_field_data_res(data_importer) # How to test this effectively?
        field_trial.res_table.reload()
        assert field_trial.res_table.item_count == expected_total[data_type]

    field_trial.res_table.reload()
    assert field_trial.res_table.item_count == expected_total["plot"]




def _temp():
    table_name = "ft_db"
    dynamodb = dynamodb_server.DynamodbServer()
    dynamodb_res = dynamodb.init_dynamodb_resources()
    field_trial = field_table.FieldTable(dynamodb_res, table_name)


    data_importer = importer.DataImporter("file_name", "meta")
    data_importer.parse_df_to_dynamo_json()

    field_trial.import_batch_field_data_res(data_importer)


    TEST_DATA_DIR = "./tests/test_data"
    dynamo_config = {'ReturnConsumedCapacity': "INDEXES" }#"Total"}



    data_type = "yield"
    file_name = os.path.join(TEST_DATA_DIR, f"test_{data_type}.csv")
    df = pd.read_csv(file_name)
    df.describe()
    df.dtypes


    data_importer = importer.DataImporter(file_name, data_type="plot")
    data_importer.parse_df_plot_to_dynamo_json()

    field_trial.import_batch_field_data_res(data_importer)

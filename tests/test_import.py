import os
from cv2 import exp
import pytest
import boto3
# import field
import importlib
import pandas as pd



from src.dynamofield.field import field_table
from src.dynamofield.field import importer
from src.dynamofield import dynamodb_init
from src.dynamofield.db import init_db, table_utils


# importlib.reload(field_table)
# importlib.reload(init_db)

@pytest.fixture
def field_trial():

    table_name = "ft_db"
    # client = dynamodb_init.init_dynamodb_client()
    # table_utils.delete_all_items(client, table_name)
    
    dynamodb_res = dynamodb_init.init_dynamodb_resources()
    field_trial = field_table.FieldTable(dynamodb_res, table_name)
    return field_trial


@pytest.mark.first
def test_creation():
    table_name = "ft_db"    
    client = dynamodb_init.init_dynamodb_client()
    init_num_table = len(client.list_tables()["TableNames"])
    if init_num_table == 0:
        init_num_table = 1
    init_db.remove_table(client, table_name)
    del_length = len(client.list_tables()["TableNames"])
    assert del_length == init_num_table - 1

    init_db.init_db_table(client, table_name)
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
    



def _temp():
    table_name = "ft_db"
    dynamodb_res = dynamodb_init.init_dynamodb_resources()
    field_trial = field_table.FieldTable(dynamodb_res, table_name)



    data_import = importer.DataImporter(file_name, "meta")
    dynamo_json_list = data_import.parse_df_to_dynamo_json()

    field_trial.batch_import_field_data_res(dynamo_json_list)


    TEST_DATA_DIR = "./tests/test_data"
    dynamo_config = {'ReturnConsumedCapacity': "INDEXES" }#"Total"}



    data_type = "yield"
    file_name = os.path.join(TEST_DATA_DIR, f"test_{data_type}.csv")
    df = pd.read_csv(file_name)
    df.describe()
    df.dtypes


    data_import = importer.DataImporter(file_name, data_type="plot")
    dynamo_json_list = data_import.parse_df_plot_to_dynamo_json()

    field_trial.batch_import_field_data_res(dynamo_json_list)


def test_import(field_trial):
  
    
    TEST_DATA_DIR = "./tests/test_data"
    expected_length = {
        "trt": 18,
        "contact": 3,
        "meta": 3,
        "management": 12,
        "plot":72
    }
    expected_count = {
        "trt": 18,
        "contact": 21,
        "meta": 24,
        "management": 36,
        "plot": 108
    }

    # for data_type in ["trt", "trial_meta", "trial_contact", "trial_management"]:
    field_trial.res_table.reload()
    assert field_trial.res_table.item_count == 0
    for data_type in expected_length.keys():
        print(data_type)
        file_name = os.path.join(TEST_DATA_DIR, f"test_{data_type}.csv")
        data_import = importer.DataImporter(file_name, data_type)
        dynamo_json_list = data_import.parse_df_to_dynamo_json()
        assert len(dynamo_json_list) == expected_length[data_type]
        field_trial.batch_import_field_data_res(dynamo_json_list) # How to test this effectively?
        field_trial.res_table.reload()
        assert field_trial.res_table.item_count == expected_count[data_type]
    
    field_trial.res_table.reload()
    assert field_trial.res_table.item_count == 108



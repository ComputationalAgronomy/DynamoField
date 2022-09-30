import os
import pytest
import boto3
# import field
import importlib
import pandas as pd



from src.dynamofield.field import field_table
from src.dynamofield.field import importer
from src.dynamofield.field import table_util
from src.dynamofield import dynamodb_init


# importlib.reload(field_table)
# importlib.reload(importer)

@pytest.fixture
def field_trial():

    
    table_name = "ft_db"
    # client = dynamodb_init.init_dynamodb_client()
    # table_util.delete_all_items(client, table_name)
    
    dynamodb_res = dynamodb_init.init_dynamodb_resources()
    field_trial = field_table.FieldTable(dynamodb_res, table_name)
    return field_trial



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
        "meta": 3,
        "contact": 3
    }
    expected_count = {
        "trt": 18,
        "meta": 21,
        "contact": 24
    }
    # for data_type in ["trt", "trial_meta", "trial_contact", "trial_management"]:
    for data_type in ["trt", "meta", "contact"]:
        file_name = os.path.join(TEST_DATA_DIR, f"test_{data_type}.csv")
        data_import = importer.DataImporter(file_name, data_type)
        dynamo_json_list = data_import.parse_df_to_dynamo_json()
        assert len(dynamo_json_list) == expected_length[data_type]
        field_trial.batch_import_field_data_res(dynamo_json_list) # How to test this effectively?
        # assert field_trial.res_table.item_count == expected_count[data_type]
        


def _test_batch():

    dynamo_json_list = parse_df_to_dynamo_json(df, sort_key_prefix="meta")
    batch_import_field_data_res(res_table, dynamo_json_list)


    import_field_data_client(client, table_name, dynamo_json_list, dynamo_config)


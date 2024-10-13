
import pytest
from dynamofield.db import dynamodb_server
from dynamofield.field import field_table


@pytest.fixture
def field_trial():

    table_name = "ft_db"
    # client = dynamodb_init.init_dynamodb_client()
    # table_utils.delete_all_items(client, table_name)
    dynamodb = dynamodb_server.DynamodbServer()
    # client = dynamodb_server.init_dynamodb_client()
    # dynamodb_res = dynamodb.init_dynamodb_resources()
    field_trial = field_table.FieldTable(dynamodb.dynamodb_res, table_name)
    return field_trial




def test_list_all_keys(field_trial: field_table.FieldTable):

    expected_key = "__private_list_all_id__"
    assert field_table.FieldTable.TRIAL_ID_LIST_PARTITION_KEY == expected_key

    expected_ids = ['trial_2B', 'trial_3C', 'trial_4D']
    results = field_trial.query_by_single_trial_id(field_table.FieldTable.TRIAL_ID_LIST_PARTITION_KEY)
    expected = [{'field_trial_id': '__private_list_all_id__', 'record_type': t} for t in expected_ids]
    assert results == expected

    results = field_trial.get_all_trial_id()
    assert results == expected_ids


import pytest

from decimal import Decimal
import boto3
import importlib
import pandas as pd
import numpy as np
from pandas.testing import assert_frame_equal

from src.dynamofield.field import field_table
from dynamofield.db import dynamodb_init

# importlib.reload(field_table)


@pytest.fixture
def field_trial():
    table_name = "ft_db"
    dynamodb_server = dynamodb_init.DynamodbServer()
    dynamodb_res = dynamodb_server.init_dynamodb_resources()
    field_trial = field_table.FieldTable(dynamodb_res, table_name)
    # field_trial = dynamodb_server.init_dynamodb_resources_table(table_name)
    return field_trial


def test_get_by_trial_id(field_trial):
    # field_trial = field_trial
    trial_id = ["trial_3C", "trial_2B"]
    trial_id = "trial_3C"
    trial_id = "trial_2B"


    result = field_trial.get_by_trial_id(trial_id)
    expected = [{'trial_id': 'trial_2B', 'phone': '234-567-890', 'person': 'John', 'info': 'contact_0'},
        {'trial_id': 'trial_2B', 'phone': '234-567-891', 'person': 'Jane', 'info': 'contact_1'},
        {'trial_id': 'trial_2B', 'amount': Decimal('14.1'), 'solid_or_powder': 'solid', 'type': 'NPK_1', 'fertilizer': 'N', 'info': 'management_0'},
        {'trial_id': 'trial_2B', 'amount': Decimal('14.7'), 'solid_or_powder': 'powder', 'type': 'NPK_2', 'fertilizer': 'N', 'info': 'management_1'},
        {'trial_id': 'trial_2B', 'amount': Decimal('37.1'), 'solid_or_powder': 'solid', 'fertilizer': 'P', 'info': 'management_2'},
        {'trial_id': 'trial_2B', 'amount': Decimal('33'), 'solid_or_powder': 'solid', 'fertilizer': 'P', 'info': 'management_3'},
        {'soil_ph': Decimal('5.2'), 'trial_id': 'trial_2B', 'soil_type': 'sandy', 'location': 'Loc_0', 'irrigation': 'No', 'info': 'meta_0'},
        {'trial_id': 'trial_2B', 'treatment': 'T1', 'seed': 'seed_type_A', 'info': 'trt_0', 'treatment_name': 'trt_1X'},
        {'trial_id': 'trial_2B', 'treatment': 'T2', 'seed': 'seed_type_A', 'info': 'trt_1', 'treatment_name': 'trt_2X'},
        {'trial_id': 'trial_2B', 'treatment': 'T3', 'seed': 'seed_type_A', 'info': 'trt_2', 'treatment_name': 'trt_3X'},
        {'trial_id': 'trial_2B', 'treatment': 'T4', 'seed': 'seed_type_A', 'info': 'trt_3', 'treatment_name': 'trt_4X'},
        {'trial_id': 'trial_2B', 'treatment': 'T5', 'seed': 'seed_type_A', 'info': 'trt_4', 'treatment_name': 'trt_5X'},
        {'trial_id': 'trial_2B', 'treatment': 'T6', 'seed': 'seed_type_A', 'info': 'trt_5', 'treatment_name': 'trt_6X'}]
    result_subset = [x for x in result if not x["info"].startswith("plot")]
    result_subset = sorted(result_subset, key=lambda x : x["info"])
    assert result_subset == expected

    # field_trial.get_by_trial_id(trial_id=["trial_3C", "trial_2B"], sort_key="plot_0202") # TOFIX

def test_get_by_trial_id_sort_key(field_trial):

    trial_id = "trial_2B"
    result = field_trial.get_by_trial_id(trial_id=trial_id, sort_key="meta_0")
    expected = [{'soil_ph': Decimal('5.2'), 'trial_id': 'trial_2B', 'soil_type': 'sandy', 'location': 'Loc_0', 'irrigation': 'No', 'info': 'meta_0'}]
    assert result == expected

    result = field_trial.get_by_trial_id(trial_id=trial_id, sort_key="contact_0")
    expected = [{'trial_id': 'trial_2B', 'phone': '234-567-890', 'person': 'John', 'info': 'contact_0'}]
    assert result == expected

    
    result = field_trial.get_by_trial_id(trial_id, sort_key="management_1")
    expected = [{'trial_id': 'trial_2B', 'amount': Decimal('14.7'), 'solid_or_powder': 'powder', 'type': 'NPK_2', 'fertilizer': 'N', 'info': 'management_1'}]
    assert result == expected

    result = field_trial.get_by_trial_id(trial_id, sort_key="management")
    assert result == []

    result = field_trial.get_by_trial_id(trial_id, sort_key="aoeuXYZ")
    assert result == []


def test_list_all_sort_keys(field_trial):
    # field_trial = field_trial
    trial_id = ["trial_3C", "trial_2B"]
    trial_id = "trial_3C"
    trial_id = "trial_2B"

    list_sort_key = field_trial.list_all_sort_keys(trial_id)
    expected = ['contact_0', 'contact_1', 'management_0', 'management_1', 'management_2', 'management_3', 'meta_0',
                'plot_1-1', 'plot_1-2', 'plot_1-3', 'plot_1-4', 'plot_1-5', 'plot_1-6', 'plot_2-1', 'plot_2-2', 'plot_2-3', 'plot_2-4', 'plot_2-5', 'plot_2-6', 'plot_3-1', 'plot_3-2', 'plot_3-3', 'plot_3-4', 'plot_3-5', 'plot_3-6', 'plot_4-1', 'plot_4-2', 'plot_4-3', 'plot_4-4', 'plot_4-5', 'plot_4-6',
                'trt_0', 'trt_1', 'trt_2', 'trt_3', 'trt_4', 'trt_5']
    assert list_sort_key == expected

    list_sort_key = field_trial.list_all_sort_keys(trial_id, prune_common=True)
    expected = ['contact_0', 'contact_1', 'management_0', 'management_1', 'management_2', 'management_3', 'meta_0']
    assert list_sort_key == expected



def test_get_all_non_standard_info(field_trial):
    
    trial_id = "trial_2B"
    result = field_trial.get_all_non_standard_info(trial_id)
    expected = {'contact_0': [{'trial_id': 'trial_2B', 'phone': '234-567-890', 'person': 'John', 'info': 'contact_0'}], 
        'contact_1': [{'trial_id': 'trial_2B', 'phone': '234-567-891', 'person': 'Jane', 'info': 'contact_1'}],
        'management_0': [{'trial_id': 'trial_2B', 'amount': Decimal('14.1'), 'solid_or_powder': 'solid', 'type': 'NPK_1', 'fertilizer': 'N', 'info': 'management_0'}],
        'management_1': [{'trial_id': 'trial_2B', 'amount': Decimal('14.7'), 'solid_or_powder': 'powder', 'type': 'NPK_2', 'fertilizer': 'N', 'info': 'management_1'}],
        'management_2': [{'trial_id': 'trial_2B', 'amount': Decimal('37.1'), 'solid_or_powder': 'solid', 'fertilizer': 'P', 'info': 'management_2'}],
        'management_3': [{'trial_id': 'trial_2B', 'amount': Decimal('33'), 'solid_or_powder': 'solid', 'fertilizer': 'P', 'info': 'management_3'}],
        'meta_0': [{'soil_ph': Decimal('5.2'), 'trial_id': 'trial_2B', 'soil_type': 'sandy', 'location': 'Loc_0', 'irrigation': 'No', 'info': 'meta_0'}]
        }
    assert result == expected



def test_get_by_sort_key_exact(field_trial):

    sort_key = "management"
    result = field_trial.get_by_sort_key(sort_key, exact=True)
    # assert_frame_equal(result, expected)
    assert result.empty
    
    sort_key = "contact_0"
    result = field_trial.get_by_sort_key(sort_key, exact=True)
    data = {'trial_id': {0: 'trial_4D', 1: 'trial_3C', 2: 'trial_2B'},
            'phone': {0: '456-789-012', 1: '345-678-901', 2: '234-567-890'},
            'person': {0: 'Jane', 1: 'Jane', 2: 'John'},
            'info': {0: 'contact_0', 1: 'contact_0', 2: 'contact_0'}}
    expected = pd.DataFrame(data)
    assert_frame_equal(result, expected)

    sort_key = "contact_1"
    result = field_trial.get_by_sort_key(sort_key, exact=True)
    data = {'trial_id': {0: 'trial_2B'},
            'phone': {0: '234-567-891'},
            'person': {0: 'Jane'},
            'info': {0: 'contact_1'}}
    expected = pd.DataFrame(data)
    assert_frame_equal(result, expected)


def test_get_by_sort_key(field_trial):

    sort_key = "meta"
    # sort_key = "trial_management"
    result = field_trial.get_by_sort_key(sort_key, exact=False)
    data = {'soil_ph': {0: 7.4, 1: 6.3, 2: 5.2},
            'trial_id': {0: 'trial_4D', 1: 'trial_3C', 2: 'trial_2B'},
            'soil_type': {0: 'sandy', 1: 'sandy', 2: 'sandy'},
            'location': {0: 'Loc_2', 1: 'Loc_1', 2: 'Loc_0'},
            'irrigation': {0: 'Yes', 1: 'Yes', 2: 'No'}, 
            'info': {0: 'meta_0', 1: 'meta_0', 2: 'meta_0'}
            }
    expected = pd.DataFrame(data)
    assert_frame_equal(result, expected)

    sort_key = "management"
    result = field_trial.get_by_sort_key(sort_key, exact=False)
    data = {'trial_id': {0: 'trial_4D', 1: 'trial_4D', 2: 'trial_4D', 3: 'trial_4D', 4: 'trial_3C', 5: 'trial_3C', 6: 'trial_3C', 7: 'trial_3C', 8: 'trial_2B', 9: 'trial_2B', 10: 'trial_2B', 11: 'trial_2B'},
            'amount': {0: 16.4, 1: 49.8, 2: 27.3, 3: 48.0, 4: 15.7, 5: 11.3, 6: 10.4, 7: 12.0, 8: 14.1, 9: 14.7, 10: 37.1, 11: 33.0}, 
            'solid_or_powder': {0: 'solid', 1: 'powder', 2: 'solid', 3: 'solid', 4: 'solid', 5: 'powder', 6: 'solid', 7: 'solid', 8: 'solid', 9: 'powder', 10: 'solid', 11: 'solid'},
            'type': {0: 'NPK_1', 1: 'NPK_2', 2: np.nan, 3: np.nan, 4: 'NPK_1', 5: 'NPK_2', 6: np.nan, 7: np.nan, 8: 'NPK_1', 9: 'NPK_2', 10: np.nan, 11: np.nan}, 
            'fertilizer': {0: 'N', 1: 'N', 2: 'P', 3: 'P', 4: 'N', 5: 'N', 6: 'P', 7: 'P', 8: 'N', 9: 'N', 10: 'P', 11: 'P'}, 
            'info': {0: 'management_0', 1: 'management_1', 2: 'management_2', 3: 'management_3', 4: 'management_0', 5: 'management_1', 6: 'management_2', 7: 'management_3', 8: 'management_0', 9: 'management_1', 10: 'management_2', 11: 'management_3'}}
    expected = pd.DataFrame(data)
    assert_frame_equal(result, expected)




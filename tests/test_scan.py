import pytest

from decimal import Decimal
import boto3
import importlib
import pandas as pd

from src.dynamofield.field import field_table
from src.dynamofield import dynamodb_init

@pytest.fixture
def field_trial():
    table_name = "ft_db"
    dynamodb_res = dynamodb_init.init_dynamodb_resources()
    field_trial = field_table.FieldTable(dynamodb_res, table_name)
    return field_trial


def test_get_by_trial_id(field_trial):
    # field_trial = field_trial
    trial_id = ["trial_3C", "trial_2B"]
    trial_id = "trial_3C"
    trial_id = "trial_2B"


    result = field_trial.get_by_trial_id(trial_id)
    expected = [{'trial_id': 'trial_2B', 'phone': '234-567-890', 'person': 'John', 'info': 'contact'},
        {'soil_ph': Decimal('5.2'), 'trial_id': 'trial_2B', 'soil_type': 'sandy', 'location': 'Loc_0', 'irrigation': 'No', 'info': 'meta'},
        {'trial_id': 'trial_2B', 'treatment': 'T1', 'seed': 'seed_type_A', 'info': 'trt_0', 'treatment_name': 'trt_1X'},
        {'trial_id': 'trial_2B', 'treatment': 'T2', 'seed': 'seed_type_A', 'info': 'trt_1', 'treatment_name': 'trt_2X'},
        {'trial_id': 'trial_2B', 'treatment': 'T3', 'seed': 'seed_type_A', 'info': 'trt_2', 'treatment_name': 'trt_3X'},
        {'trial_id': 'trial_2B', 'treatment': 'T4', 'seed': 'seed_type_A', 'info': 'trt_3', 'treatment_name': 'trt_4X'},
        {'trial_id': 'trial_2B', 'treatment': 'T5', 'seed': 'seed_type_A', 'info': 'trt_4', 'treatment_name': 'trt_5X'},
        {'trial_id': 'trial_2B', 'treatment': 'T6', 'seed': 'seed_type_A', 'info': 'trt_5', 'treatment_name': 'trt_6X'}]
    assert result == expected
    # field_trial.get_by_trial_id(trial_id=["trial_3C", "trial_2B"], sort_key="plot_0202") # TOFIX

    result = field_trial.get_by_trial_id(trial_id=trial_id, sort_key="meta")
    expected = [{'soil_ph': Decimal('5.2'), 'trial_id': 'trial_2B', 'soil_type': 'sandy', 'location': 'Loc_0', 'irrigation': 'No', 'info': 'meta'}]
    assert result == expected

    result = field_trial.get_by_trial_id(trial_id=trial_id, sort_key="contact")
    expected = [{'trial_id': 'trial_2B', 'phone': '234-567-890', 'person': 'John', 'info': 'contact'}]
    assert result == expected


    field_trial.get_by_trial_id(trial_id, sort_key="aoeu")


def test_get_by_trial_id(field_trial):
    # field_trial = field_trial
    trial_id = ["trial_3C", "trial_2B"]
    trial_id = "trial_3C"
    trial_id = "trial_2B"


    list_sort_key = field_trial.list_all_sort_keys(trial_id)
    expected = ['contact', 'meta', 'trt_0', 'trt_1', 'trt_2', 'trt_3', 'trt_4', 'trt_5']
    assert list_sort_key == expected


    list_sort_key = field_trial.list_all_sort_keys(trial_id, prune_common=True)
    expected = ['contact', 'meta']
    assert list_sort_key == expected



def test_get_all_non_standard_info(field_trial):
    
    trial_id = "trial_2B"
    result = field_trial.get_all_non_standard_info(trial_id)
    expected = {'contact': [{'trial_id': 'trial_2B', 'phone': '234-567-890', 'person': 'John', 'info': 'contact'}], 
        'meta': [{'soil_ph': Decimal('5.2'), 'trial_id': 'trial_2B', 'soil_type': 'sandy', 'location': 'Loc_0', 'irrigation': 'No', 'info': 'meta'}]}
    assert result == expected



def get_by_sort_key(field_trial):

    sort_key = "meta"
    # sort_key = "trial_management"
    field_trial.get_by_sort_key(sort_key, type="begins")

    sort_key = "contact"
    field_trial.get_by_sort_key(sort_key)


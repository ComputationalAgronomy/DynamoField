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
    dynamodb = dynamodb_init.DynamodbServer()
    field_trial = field_table.FieldTable(dynamodb.dynamodb_res, table_name)
    return field_trial


def test_query_df_all_plots(field_trial: field_table.FieldTable):
    trial_id = "trial_2B"
    df_plot = field_trial.query_df_all_plots(trial_id)
    df_trt = field_trial.query_df_all_treatments(trial_id)
    df_merged = pd.merge(df_plot, df_trt, how="inner", on=["trial_id", "treatment"])
    
    df_plot_trt = field_trial.query_df_plot_treatment(trial_id)
    data = {
        'trial_id': {0: 'trial_2B', 1: 'trial_2B', 2: 'trial_2B', 3: 'trial_2B', 4: 'trial_2B', 5: 'trial_2B', 6: 'trial_2B', 7: 'trial_2B', 8: 'trial_2B', 9: 'trial_2B', 10: 'trial_2B', 11: 'trial_2B', 12: 'trial_2B', 13: 'trial_2B', 14: 'trial_2B', 15: 'trial_2B', 16: 'trial_2B', 17: 'trial_2B', 18: 'trial_2B', 19: 'trial_2B', 20: 'trial_2B', 21: 'trial_2B', 22: 'trial_2B', 23: 'trial_2B'}, 
        'info_x': {0: 'plot_1-1', 1: 'plot_1-5', 2: 'plot_2-3', 3: 'plot_4-2', 4: 'plot_1-2', 5: 'plot_1-6', 6: 'plot_2-5', 7: 'plot_3-3', 8: 'plot_1-3', 9: 'plot_2-1', 10: 'plot_4-3', 11: 'plot_4-5', 12: 'plot_1-4', 13: 'plot_3-1', 14: 'plot_3-2', 15: 'plot_4-4', 16: 'plot_2-2', 17: 'plot_3-4', 18: 'plot_3-6', 19: 'plot_4-1', 20: 'plot_2-4', 21: 'plot_2-6', 22: 'plot_3-5', 23: 'plot_4-6'}, 
        'treatment': {0: 'T3', 1: 'T3', 2: 'T3', 3: 'T3', 4: 'T1', 5: 'T1', 6: 'T1', 7: 'T1', 8: 'T4', 9: 'T4', 10: 'T4', 11: 'T4', 12: 'T6', 13: 'T6', 14: 'T6', 15: 'T6', 16: 'T5', 17: 'T5', 18: 'T5', 19: 'T5', 20: 'T2', 21: 'T2', 22: 'T2', 23: 'T2'}, 
        'meta': {0: 9.6, 1: 5.2, 2: 9.3, 3: 3.5, 4: 6.2, 5: 8.2, 6: 2.6, 7: 5.9, 8: 1.2, 9: 4.2, 10: 6.5, 11: 2.7, 12: 9.2, 13: 2.8, 14: 9.8, 15: 4.2, 16: 7.6, 17: 8.9, 18: 1.3, 19: 6.0, 20: 5.7, 21: 2.0, 22: 4.8, 23: 7.5}, 'yields': {0: 51.25, 1: 84.98, 2: 88.33, 3: 88.92, 4: 56.06, 5: 70.02, 6: 93.21, 7: 89.26, 8: 69.76, 9: 78.08, 10: 68.19, 11: 96.49, 12: 96.23, 13: 82.13, 14: 66.0, 15: 98.25, 16: 73.6, 17: 65.49, 18: 50.01, 19: 52.25, 20: 96.39, 21: 94.05, 22: 77.3, 23: 54.32}, 
        'info_y': {0: 'trt_2', 1: 'trt_2', 2: 'trt_2', 3: 'trt_2', 4: 'trt_0', 5: 'trt_0', 6: 'trt_0', 7: 'trt_0', 8: 'trt_3', 9: 'trt_3', 10: 'trt_3', 11: 'trt_3', 12: 'trt_5', 13: 'trt_5', 14: 'trt_5', 15: 'trt_5', 16: 'trt_4', 17: 'trt_4', 18: 'trt_4', 19: 'trt_4', 20: 'trt_1', 21: 'trt_1', 22: 'trt_1', 23: 'trt_1'}, 
        'seed': {0: 'seed_type_A', 1: 'seed_type_A', 2: 'seed_type_A', 3: 'seed_type_A', 4: 'seed_type_A', 5: 'seed_type_A', 6: 'seed_type_A', 7: 'seed_type_A', 8: 'seed_type_A', 9: 'seed_type_A', 10: 'seed_type_A', 11: 'seed_type_A', 12: 'seed_type_A', 13: 'seed_type_A', 14: 'seed_type_A', 15: 'seed_type_A', 16: 'seed_type_A', 17: 'seed_type_A', 18: 'seed_type_A', 19: 'seed_type_A', 20: 'seed_type_A', 21: 'seed_type_A', 22: 'seed_type_A', 23: 'seed_type_A'}, 
        'treatment_name': {0: 'trt_3X', 1: 'trt_3X', 2: 'trt_3X', 3: 'trt_3X', 4: 'trt_1X', 5: 'trt_1X', 6: 'trt_1X', 7: 'trt_1X', 8: 'trt_4X', 9: 'trt_4X', 10: 'trt_4X', 11: 'trt_4X', 12: 'trt_6X', 13: 'trt_6X', 14: 'trt_6X', 15: 'trt_6X', 16: 'trt_5X', 17: 'trt_5X', 18: 'trt_5X', 19: 'trt_5X', 20: 'trt_2X', 21: 'trt_2X', 22: 'trt_2X', 23: 'trt_2X'}
    }
    expected = pd.DataFrame(data)
    assert_frame_equal(df_plot_trt, expected)
    assert_frame_equal(df_merged, df_plot_trt)
    



def test_query_df_all_plots(field_trial: field_table.FieldTable):
    trial_id = "trial_2B"
    df_plot_trt = field_trial.query_df_plot_treatment(trial_id)
    df_get_two_info = field_trial.query_df_by_two_sort_keys(
            trial_id, "plot", "trt", merged_by="treatment")
    assert_frame_equal(df_plot_trt, df_get_two_info)



def test_query_df_all_plots(field_trial: field_table.FieldTable):
    trial_id = "trial_2B"
    df_plot = field_trial.query_df_all_plots(trial_id)
    df_trt = field_trial.query_df_all_treatments(trial_id)
    df_merged = pd.merge(df_trt, df_plot, how="inner", on=["trial_id", "treatment"])
    
    df_get_two_info = field_trial.query_df_by_two_sort_keys(
            trial_id, "trt", "plot", merged_by="treatment")
    assert_frame_equal(df_merged, df_get_two_info)

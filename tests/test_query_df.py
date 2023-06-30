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


def test_query_df_all_plots_treatments(field_trial: field_table.FieldTable):
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
    

def test_query_df_all_plots_treatments_2(field_trial: field_table.FieldTable):
    trial_id = "trial_2B"
    df_plot = field_trial.query_df_all_plots(trial_id)
    df_trt = field_trial.query_df_all_treatments(trial_id)
    df_merged = pd.merge(df_trt, df_plot, how="inner", on=["trial_id", "treatment"])
    
    df_get_two_info = field_trial.query_df_by_two_sort_keys(
            trial_id, "trt", "plot", merged_by="treatment")
    assert_frame_equal(df_merged, df_get_two_info)




def test_query_df_all_plots(field_trial: field_table.FieldTable):
    trial_id = "trial_2B"
    df_plot_trt = field_trial.query_df_plot_treatment(trial_id)
    df_get_two_info = field_trial.query_df_by_two_sort_keys(
            trial_id, "plot", "trt", merged_by="treatment")
    assert_frame_equal(df_plot_trt, df_get_two_info)






def test_query_df_all_plots_multi(field_trial: field_table.FieldTable):

    trial_ids = ["trial_2B", "trial_3C"]
    df_plots = field_trial.query_df_all_plots(trial_ids)
    data = {'trial_id': {0: 'trial_2B', 1: 'trial_2B', 2: 'trial_2B', 3: 'trial_2B', 4: 'trial_2B', 5: 'trial_2B', 6: 'trial_2B', 7: 'trial_2B', 8: 'trial_2B', 9: 'trial_2B', 10: 'trial_2B', 11: 'trial_2B', 12: 'trial_2B', 13: 'trial_2B', 14: 'trial_2B', 15: 'trial_2B', 16: 'trial_2B', 17: 'trial_2B', 18: 'trial_2B', 19: 'trial_2B', 20: 'trial_2B', 21: 'trial_2B', 22: 'trial_2B', 23: 'trial_2B', 24: 'trial_3C', 25: 'trial_3C', 26: 'trial_3C', 27: 'trial_3C', 28: 'trial_3C', 29: 'trial_3C', 30: 'trial_3C', 31: 'trial_3C', 32: 'trial_3C', 33: 'trial_3C', 34: 'trial_3C', 35: 'trial_3C', 36: 'trial_3C', 37: 'trial_3C', 38: 'trial_3C', 39: 'trial_3C', 40: 'trial_3C', 41: 'trial_3C', 42: 'trial_3C', 43: 'trial_3C', 44: 'trial_3C', 45: 'trial_3C', 46: 'trial_3C', 47: 'trial_3C'}, 
            'info': {0: 'plot_1-1', 1: 'plot_1-2', 2: 'plot_1-3', 3: 'plot_1-4', 4: 'plot_1-5', 5: 'plot_1-6', 6: 'plot_2-1', 7: 'plot_2-2', 8: 'plot_2-3', 9: 'plot_2-4', 10: 'plot_2-5', 11: 'plot_2-6', 12: 'plot_3-1', 13: 'plot_3-2', 14: 'plot_3-3', 15: 'plot_3-4', 16: 'plot_3-5', 17: 'plot_3-6', 18: 'plot_4-1', 19: 'plot_4-2', 20: 'plot_4-3', 21: 'plot_4-4', 22: 'plot_4-5', 23: 'plot_4-6', 24: 'plot_1-1', 25: 'plot_1-2', 26: 'plot_1-3', 27: 'plot_1-4', 28: 'plot_1-5', 29: 'plot_1-6', 30: 'plot_2-1', 31: 'plot_2-2', 32: 'plot_2-3', 33: 'plot_2-4', 34: 'plot_2-5', 35: 'plot_2-6', 36: 'plot_3-1', 37: 'plot_3-2', 38: 'plot_3-3', 39: 'plot_3-4', 40: 'plot_3-5', 41: 'plot_3-6', 42: 'plot_4-1', 43: 'plot_4-2', 44: 'plot_4-3', 45: 'plot_4-4', 46: 'plot_4-5', 47: 'plot_4-6'}, 
            'treatment': {0: 'T3', 1: 'T1', 2: 'T4', 3: 'T6', 4: 'T3', 5: 'T1', 6: 'T4', 7: 'T5', 8: 'T3', 9: 'T2', 10: 'T1', 11: 'T2', 12: 'T6', 13: 'T6', 14: 'T1', 15: 'T5', 16: 'T2', 17: 'T5', 18: 'T5', 19: 'T3', 20: 'T4', 21: 'T6', 22: 'T4', 23: 'T2', 24: 'T4', 25: 'T4', 26: 'T6', 27: 'T3', 28: 'T2', 29: 'T5', 30: 'T1', 31: 'T2', 32: 'T2', 33: 'T5', 34: 'T5', 35: 'T1', 36: 'T4', 37: 'T6', 38: 'T3', 39: 'T2', 40: 'T3', 41: 'T4', 42: 'T1', 43: 'T6', 44: 'T5', 45: 'T3', 46: 'T6', 47: 'T1'}, 
            # 'plot': {0: 'plot_1-1', 1: 'plot_1-2', 2: 'plot_1-3', 3: 'plot_1-4', 4: 'plot_1-5', 5: 'plot_1-6', 6: 'plot_2-1', 7: 'plot_2-2', 8: 'plot_2-3', 9: 'plot_2-4', 10: 'plot_2-5', 11: 'plot_2-6', 12: 'plot_3-1', 13: 'plot_3-2', 14: 'plot_3-3', 15: 'plot_3-4', 16: 'plot_3-5', 17: 'plot_3-6', 18: 'plot_4-1', 19: 'plot_4-2', 20: 'plot_4-3', 21: 'plot_4-4', 22: 'plot_4-5', 23: 'plot_4-6', 24: 'plot_1-1', 25: 'plot_1-2', 26: 'plot_1-3', 27: 'plot_1-4', 28: 'plot_1-5', 29: 'plot_1-6', 30: 'plot_2-1', 31: 'plot_2-2', 32: 'plot_2-3', 33: 'plot_2-4', 34: 'plot_2-5', 35: 'plot_2-6', 36: 'plot_3-1', 37: 'plot_3-2', 38: 'plot_3-3', 39: 'plot_3-4', 40: 'plot_3-5', 41: 'plot_3-6', 42: 'plot_4-1', 43: 'plot_4-2', 44: 'plot_4-3', 45: 'plot_4-4', 46: 'plot_4-5', 47: 'plot_4-6'}, 
            'meta': {0: 9.6, 1: 6.2, 2: 1.2, 3: 9.2, 4: 5.2, 5: 8.2, 6: 4.2, 7: 7.6, 8: 9.3, 9: 5.7, 10: 2.6, 11: 2.0, 12: 2.8, 13: 9.8, 14: 5.9, 15: 8.9, 16: 4.8, 17: 1.3, 18: 6.0, 19: 3.5, 20: 6.5, 21: 4.2, 22: 2.7, 23: 7.5, 24: 5.5, 25: 5.6, 26: 3.4, 27: 10.0, 28: 9.3, 29: 7.4, 30: 7.0, 31: 9.3, 32: 1.8, 33: 9.2, 34: 3.4, 35: 2.2, 36: 3.7, 37: 8.3, 38: 3.9, 39: 4.7, 40: 4.8, 41: 5.2, 42: 6.3, 43: 7.0, 44: 6.3, 45: 9.3, 46: 4.4, 47: 2.5}, 
            'yields': {0: 51.25, 1: 56.06, 2: 69.76, 3: 96.23, 4: 84.98, 5: 70.02, 6: 78.08, 7: 73.6, 8: 88.33, 9: 96.39, 10: 93.21, 11: 94.05, 12: 82.13, 13: 66.0, 14: 89.26, 15: 65.49, 16: 77.3, 17: 50.01, 18: 52.25, 19: 88.92, 20: 68.19, 21: 98.25, 22: 96.49, 23: 54.32, 24: 58.43, 25: 96.53, 26: 73.82, 27: 65.84, 28: 78.15, 29: 76.04, 30: 81.65, 31: 51.63, 32: 51.9, 33: 86.16, 34: 69.31, 35: 80.07, 36: 73.2, 37: 66.27, 38: 57.62, 39: 71.1, 40: 67.48, 41: 81.89, 42: 63.81, 43: 92.6, 44: 50.16, 45: 89.01, 46: 80.46, 47: 80.1}}
    expected = pd.DataFrame(data)
    assert_frame_equal(df_plots, expected)



def test_query_df_all_trt(field_trial: field_table.FieldTable):
    
    trial_id = "trial_2B"
    df_trt = field_trial.query_df_all_treatments(trial_id)
    data = {'trial_id': {0: 'trial_2B', 1: 'trial_2B', 2: 'trial_2B', 3: 'trial_2B', 4: 'trial_2B', 5: 'trial_2B'},
            'info': {0: 'trt_0', 1: 'trt_1', 2: 'trt_2', 3: 'trt_3', 4: 'trt_4', 5: 'trt_5'},
            'treatment': {0: 'T1', 1: 'T2', 2: 'T3', 3: 'T4', 4: 'T5', 5: 'T6'},
            'seed': {0: 'seed_type_A', 1: 'seed_type_A', 2: 'seed_type_A', 3: 'seed_type_A', 4: 'seed_type_A', 5: 'seed_type_A'},
            'treatment_name': {0: 'trt_1X', 1: 'trt_2X', 2: 'trt_3X', 3: 'trt_4X', 4: 'trt_5X', 5: 'trt_6X'}}
    expected = pd.DataFrame(data)
    assert_frame_equal(df_trt, expected)



def test_query_df_all_trt_multi(field_trial: field_table.FieldTable):
    
    trial_ids = ["trial_2B", "trial_3C"]
    df_trt = field_trial.query_df_all_treatments(trial_ids)
    data = {'trial_id': {0: 'trial_2B', 1: 'trial_2B', 2: 'trial_2B', 3: 'trial_2B', 4: 'trial_2B', 5: 'trial_2B', 6: 'trial_3C', 7: 'trial_3C', 8: 'trial_3C', 9: 'trial_3C', 10: 'trial_3C', 11: 'trial_3C'}, 
            'info': {0: 'trt_0', 1: 'trt_1', 2: 'trt_2', 3: 'trt_3', 4: 'trt_4', 5: 'trt_5', 6: 'trt_0', 7: 'trt_1', 8: 'trt_2', 9: 'trt_3', 10: 'trt_4', 11: 'trt_5'}, 
            'treatment': {0: 'T1', 1: 'T2', 2: 'T3', 3: 'T4', 4: 'T5', 5: 'T6', 6: 'T1', 7: 'T2', 8: 'T3', 9: 'T4', 10: 'T5', 11: 'T6'}, 
            'seed': {0: 'seed_type_A', 1: 'seed_type_A', 2: 'seed_type_A', 3: 'seed_type_A', 4: 'seed_type_A', 5: 'seed_type_A', 6: 'seed_type_B', 7: 'seed_type_B', 8: 'seed_type_B', 9: 'seed_type_B', 10: 'seed_type_B', 11: 'seed_type_B'}, 
            'treatment_name': {0: 'trt_1X', 1: 'trt_2X', 2: 'trt_3X', 3: 'trt_4X', 4: 'trt_5X', 5: 'trt_6X', 6: 'trt_1X', 7: 'trt_2X', 8: 'trt_3X', 9: 'trt_4X', 10: 'trt_5X', 11: 'trt_6X'}}
    expected = pd.DataFrame(data)
    assert_frame_equal(df_trt, expected)



import os

import numpy as np
import pandas as pd
import pytest
from boto3.dynamodb.conditions import Key
from pandas.testing import assert_frame_equal

from dynamofield.db import dynamodb_init, init_db, table_utils
from dynamofield.df import df_operation
from dynamofield.field import field_table, importer


@pytest.fixture
def df1():
    df1 = pd.DataFrame({
        'trial_id': {0: 'trial_2B', 1: 'trial_2B', 2: 'trial_2B', 3: 'trial_3C', 4: 'trial_3C', 5: 'trial_3C', 6: 'trial_2B', 7: 'trial_2B', 8: 'trial_2B', 9: 'trial_3C', 10: 'trial_3C', 11: 'trial_3C', 12: 'trial_2B', 13: 'trial_2B', 14: 'trial_2B', 15: 'trial_3C', 16: 'trial_3C', 17: 'trial_3C', 18: 'trial_2B', 19: 'trial_2B', 20: 'trial_2B', 21: 'trial_3C', 22: 'trial_3C', 23: 'trial_3C'},
        'info': {0: 'trt_0', 1: 'trt_1', 2: 'trt_2', 3: 'trt_0', 4: 'trt_1', 5: 'trt_2', 6: 'chemical_0', 7: 'chemical_1', 8: 'chemical_2', 9: 'chemical_3', 10: 'chemical_4', 11: 'chemical_5', 12: 'chemical_6', 13: 'chemical_7', 14: 'chemical_8', 15: 'chemical_9', 16: 'chemical_10', 17: 'chemical_11', 18: 'chemical_12', 19: 'chemical_13', 20: 'chemical_14', 21: 'chemical_15', 22: 'chemical_16', 23: 'chemical_17'},
        'treatment': {0: 'T1', 1: 'T2', 2: 'T3', 3: 'T1', 4: 'T2', 5: 'T3', 6: 'T1', 7: 'T2', 8: 'T3', 9: 'T1', 10: 'T2', 11: 'T3', 12: 'T1', 13: 'T2', 14: 'T3', 15: 'T1', 16: 'T2', 17: 'T3', 18: 'T1', 19: 'T2', 20: 'T3', 21: 'T1', 22: 'T2', 23: 'T3'},
        'treatment_name': {0: 'trt_1X', 1: 'trt_2X', 2: 'trt_3X', 3: 'trt_1X', 4: 'trt_2X', 5: 'trt_3X', 6: np.nan, 7: np.nan, 8: np.nan, 9: np.nan, 10: np.nan, 11: np.nan, 12: np.nan, 13: np.nan, 14: np.nan, 15: np.nan, 16: np.nan, 17: np.nan, 18: np.nan, 19: np.nan, 20: np.nan, 21: np.nan, 22: np.nan, 23: np.nan},
        'chemical': {0: np.nan, 1: np.nan, 2: np.nan, 3: np.nan, 4: np.nan, 5: np.nan, 6: 0.0, 7: 0.0, 8: 0.0, 9: 0.0, 10: 0.0, 11: 0.0, 12: 1.0, 13: 1.0, 14: 1.0, 15: 1.0, 16: 1.0, 17: 1.0, 18: 2.0, 19: 2.0, 20: 2.0, 21: 3.0, 22: 3.0, 23: 3.0},
        'trt_type': {0: np.nan, 1: np.nan, 2: np.nan, 3: np.nan, 4: np.nan, 5: np.nan, 6: 'T3', 7: 'T2', 8: 'T1', 9: 'T3', 10: 'T2', 11: 'T1', 12: 'T3', 13: 'T2', 14: 'T1', 15: 'T3', 16: 'T2', 17: 'T1', 18: 'T3', 19: 'T2', 20: 'T1', 21: 'T3', 22: 'T2', 23: 'T1'},
    })

    return df1


@pytest.fixture
def df2():
    df2 = pd.DataFrame({
        'trial_id': {0: 'trial_2B', 1: 'trial_2B', 2: 'trial_3C', 3: 'trial_3C', 4: 'trial_3C', 5: 'trial_4D', 6: 'trial_4D', 7: 'trial_4D'},
        'Fertilizer': {0: 'NPK', 1: 'NPK50', 2: np.nan, 3: np.nan, 4: np.nan, 5: np.nan, 6: np.nan, 7: np.nan},
        'ferterlizer_usage': {0: np.nan, 1: np.nan, 2: 'NPK', 3: 'NPK50', 4: 'N80', 5: np.nan, 6: np.nan, 7: np.nan},
        'type_chemical': {0: np.nan, 1: np.nan, 2: np.nan, 3: np.nan, 4: np.nan, 5: 'N50P30', 6: 'NPK', 7: 'N50P30'},
        'Date_DOP': {0: 10, 1: 20, 2: 15, 3: 25, 4: 35, 5: 11, 6: 22, 7: 33}
    })
    return df2


def test_merge(df1: pd.DataFrame):

    result = df_operation.merge_df(df1, "trt", "chemical", "treatment", "treatment")
    data = {'trial_id': {0: 'trial_2B', 1: 'trial_2B', 2: 'trial_2B', 3: 'trial_2B', 4: 'trial_2B', 5: 'trial_2B', 6: 'trial_2B', 7: 'trial_2B', 8: 'trial_2B', 9: 'trial_3C', 10: 'trial_3C', 11: 'trial_3C', 12: 'trial_3C', 13: 'trial_3C', 14: 'trial_3C', 15: 'trial_3C', 16: 'trial_3C', 17: 'trial_3C'}, 'info_t1': {0: 'trt_0', 1: 'trt_0', 2: 'trt_0', 3: 'trt_1', 4: 'trt_1', 5: 'trt_1', 6: 'trt_2', 7: 'trt_2', 8: 'trt_2', 9: 'trt_0', 10: 'trt_0', 11: 'trt_0', 12: 'trt_1', 13: 'trt_1', 14: 'trt_1', 15: 'trt_2', 16: 'trt_2', 17: 'trt_2'}, 'treatment': {0: 'T1', 1: 'T1', 2: 'T1', 3: 'T2', 4: 'T2', 5: 'T2', 6: 'T3', 7: 'T3', 8: 'T3', 9: 'T1', 10: 'T1', 11: 'T1', 12: 'T2', 13: 'T2', 14: 'T2', 15: 'T3', 16: 'T3', 17: 'T3'}, 'treatment_name': {0: 'trt_1X', 1: 'trt_1X', 2: 'trt_1X', 3: 'trt_2X', 4: 'trt_2X', 5: 'trt_2X', 6: 'trt_3X', 7: 'trt_3X', 8: 'trt_3X', 9: 'trt_1X', 10: 'trt_1X', 11: 'trt_1X', 12: 'trt_2X', 13: 'trt_2X', 14: 'trt_2X', 15: 'trt_3X', 16: 'trt_3X', 17: 'trt_3X'}, 'info_t2': {0: 'chemical_0', 1: 'chemical_6', 2: 'chemical_12', 3: 'chemical_1', 4: 'chemical_7', 5: 'chemical_13', 6: 'chemical_2', 7: 'chemical_8', 8: 'chemical_14', 9: 'chemical_3', 10: 'chemical_9', 11: 'chemical_15', 12: 'chemical_4', 13: 'chemical_10', 14: 'chemical_16', 15: 'chemical_5', 16: 'chemical_11', 17: 'chemical_17'}, 'chemical': {0: 0.0, 1: 1.0, 2: 2.0, 3: 0.0, 4: 1.0, 5: 2.0, 6: 0.0, 7: 1.0, 8: 2.0, 9: 0.0, 10: 1.0, 11: 3.0, 12: 0.0, 13: 1.0, 14: 3.0, 15: 0.0, 16: 1.0, 17: 3.0}, 'trt_type': {0: 'T3', 1: 'T3', 2: 'T3', 3: 'T2', 4: 'T2', 5: 'T2', 6: 'T1', 7: 'T1', 8: 'T1', 9: 'T3', 10: 'T3', 11: 'T3', 12: 'T2', 13: 'T2', 14: 'T2', 15: 'T1', 16: 'T1', 17: 'T1'}}
    expected = pd.DataFrame(data)
    assert_frame_equal(result, expected)


def test_merge_diff_name(df1: pd.DataFrame):
    result = df_operation.merge_df(df1, "trt", "chemical", "treatment", "trt_type")
    data = {'trial_id': {0: 'trial_2B', 1: 'trial_2B', 2: 'trial_2B', 3: 'trial_2B', 4: 'trial_2B', 5: 'trial_2B', 6: 'trial_2B', 7: 'trial_2B', 8: 'trial_2B', 9: 'trial_3C', 10: 'trial_3C', 11: 'trial_3C', 12: 'trial_3C', 13: 'trial_3C', 14: 'trial_3C', 15: 'trial_3C', 16: 'trial_3C', 17: 'trial_3C'}, 'info_t1': {0: 'trt_0', 1: 'trt_0', 2: 'trt_0', 3: 'trt_1', 4: 'trt_1', 5: 'trt_1', 6: 'trt_2', 7: 'trt_2', 8: 'trt_2', 9: 'trt_0', 10: 'trt_0', 11: 'trt_0', 12: 'trt_1', 13: 'trt_1', 14: 'trt_1', 15: 'trt_2', 16: 'trt_2', 17: 'trt_2'}, 'merge_treatment_trt_type': {0: 'T1', 1: 'T1', 2: 'T1', 3: 'T2', 4: 'T2', 5: 'T2', 6: 'T3', 7: 'T3', 8: 'T3', 9: 'T1', 10: 'T1', 11: 'T1', 12: 'T2', 13: 'T2', 14: 'T2', 15: 'T3', 16: 'T3', 17: 'T3'}, 'treatment_name': {0: 'trt_1X', 1: 'trt_1X', 2: 'trt_1X', 3: 'trt_2X', 4: 'trt_2X', 5: 'trt_2X', 6: 'trt_3X', 7: 'trt_3X', 8: 'trt_3X', 9: 'trt_1X', 10: 'trt_1X', 11: 'trt_1X', 12: 'trt_2X', 13: 'trt_2X', 14: 'trt_2X', 15: 'trt_3X', 16: 'trt_3X', 17: 'trt_3X'}, 'info_t2': {0: 'chemical_2', 1: 'chemical_8', 2: 'chemical_14', 3: 'chemical_1', 4: 'chemical_7', 5: 'chemical_13', 6: 'chemical_0', 7: 'chemical_6', 8: 'chemical_12', 9: 'chemical_5', 10: 'chemical_11', 11: 'chemical_17', 12: 'chemical_4', 13: 'chemical_10', 14: 'chemical_16', 15: 'chemical_3', 16: 'chemical_9', 17: 'chemical_15'}, 'treatment': {0: 'T3', 1: 'T3', 2: 'T3', 3: 'T2', 4: 'T2', 5: 'T2', 6: 'T1', 7: 'T1', 8: 'T1', 9: 'T3', 10: 'T3', 11: 'T3', 12: 'T2', 13: 'T2', 14: 'T2', 15: 'T1', 16: 'T1', 17: 'T1'}, 'chemical': {0: 0.0, 1: 1.0, 2: 2.0, 3: 0.0, 4: 1.0, 5: 2.0, 6: 0.0, 7: 1.0, 8: 2.0, 9: 0.0, 10: 1.0, 11: 3.0, 12: 0.0, 13: 1.0, 14: 3.0, 15: 0.0, 16: 1.0, 17: 3.0}}
    expected = pd.DataFrame(data)
    assert_frame_equal(result, expected)


def test_merge_diff_column(df1: pd.DataFrame):
    result = df_operation.merge_df(df1, "trt", "chemical", "treatment_name", "trt_type")
    data = {'trial_id': {0: 'trial_2B', 1: 'trial_2B', 2: 'trial_2B', 3: 'trial_3C', 4: 'trial_3C', 5: 'trial_3C', 6: 'trial_2B', 7: 'trial_2B', 8: 'trial_2B', 9: 'trial_2B', 10: 'trial_2B', 11: 'trial_2B', 12: 'trial_2B', 13: 'trial_2B', 14: 'trial_2B', 15: 'trial_3C', 16: 'trial_3C', 17: 'trial_3C', 18: 'trial_3C', 19: 'trial_3C', 20: 'trial_3C', 21: 'trial_3C', 22: 'trial_3C', 23: 'trial_3C'}, 'info_t1': {0: 'trt_0', 1: 'trt_1', 2: 'trt_2', 3: 'trt_0', 4: 'trt_1', 5: 'trt_2', 6: np.nan, 7: np.nan, 8: np.nan, 9: np.nan, 10: np.nan, 11: np.nan, 12: np.nan, 13: np.nan, 14: np.nan, 15: np.nan, 16: np.nan, 17: np.nan, 18: np.nan, 19: np.nan, 20: np.nan, 21: np.nan, 22: np.nan, 23: np.nan}, 'treatment_t1': {0: 'T1', 1: 'T2', 2: 'T3', 3: 'T1', 4: 'T2', 5: 'T3', 6: np.nan, 7: np.nan, 8: np.nan, 9: np.nan, 10: np.nan, 11: np.nan, 12: np.nan, 13: np.nan, 14: np.nan, 15: np.nan, 16: np.nan, 17: np.nan, 18: np.nan, 19: np.nan, 20: np.nan, 21: np.nan, 22: np.nan, 23: np.nan}, 'merge_treatment_name_trt_type': {0: 'trt_1X', 1: 'trt_2X', 2: 'trt_3X', 3: 'trt_1X', 4: 'trt_2X', 5: 'trt_3X', 6: 'T3', 7: 'T3', 8: 'T3', 9: 'T2', 10: 'T2', 11: 'T2', 12: 'T1', 13: 'T1', 14: 'T1', 15: 'T3', 16: 'T3', 17: 'T3', 18: 'T2', 19: 'T2', 20: 'T2', 21: 'T1', 22: 'T1', 23: 'T1'}, 'info_t2': {0: np.nan, 1: np.nan, 2: np.nan, 3: np.nan, 4: np.nan, 5: np.nan, 6: 'chemical_0', 7: 'chemical_6', 8: 'chemical_12', 9: 'chemical_1', 10: 'chemical_7', 11: 'chemical_13', 12: 'chemical_2', 13: 'chemical_8', 14: 'chemical_14', 15: 'chemical_3', 16: 'chemical_9', 17: 'chemical_15', 18: 'chemical_4', 19: 'chemical_10', 20: 'chemical_16', 21: 'chemical_5', 22: 'chemical_11', 23: 'chemical_17'}, 'treatment_t2': {0: np.nan, 1: np.nan, 2: np.nan, 3: np.nan, 4: np.nan, 5: np.nan, 6: 'T1', 7: 'T1', 8: 'T1', 9: 'T2', 10: 'T2', 11: 'T2', 12: 'T3', 13: 'T3', 14: 'T3', 15: 'T1', 16: 'T1', 17: 'T1', 18: 'T2', 19: 'T2', 20: 'T2', 21: 'T3', 22: 'T3', 23: 'T3'}, 'chemical': {0: np.nan, 1: np.nan, 2: np.nan, 3: np.nan, 4: np.nan, 5: np.nan, 6: 0.0, 7: 1.0, 8: 2.0, 9: 0.0, 10: 1.0, 11: 2.0, 12: 0.0, 13: 1.0, 14: 2.0, 15: 0.0, 16: 1.0, 17: 3.0, 18: 0.0, 19: 1.0, 20: 3.0, 21: 0.0, 22: 1.0, 23: 3.0}}
    expected = pd.DataFrame(data)
    assert_frame_equal(result, expected)


def test_merge_columns_same_sort_key(df2: pd.DataFrame):
    merge_columns = ['Fertilizer', 'ferterlizer_usage', 'type_chemical']
    result = df_operation.merge_multi_columns(df2, merge_columns)
    expected = pd.DataFrame({
        'trial_id': {0: 'trial_2B', 1: 'trial_2B', 2: 'trial_3C', 3: 'trial_3C', 4: 'trial_3C', 5: 'trial_4D', 6: 'trial_4D', 7: 'trial_4D'},
        'Date_DOP': {0: 10, 1: 20, 2: 15, 3: 25, 4: 35, 5: 11, 6: 22, 7: 33},
        'merged_column': {0: 'NPK', 1: 'NPK50', 2: 'NPK', 3: 'NPK50', 4: 'N80', 5: 'N50P30', 6: 'NPK', 7: 'N50P30'},
    })
    assert_frame_equal(result, expected)


def test_merge_columns_same_sort_key_partial(df2: pd.DataFrame):
    merge_columns = ['Fertilizer', 'type_chemical']
    result = df_operation.merge_multi_columns(df2, merge_columns)
    expected = pd.DataFrame({
        'trial_id': {0: 'trial_2B', 1: 'trial_2B', 2: 'trial_3C', 3: 'trial_3C', 4: 'trial_3C', 5: 'trial_4D', 6: 'trial_4D', 7: 'trial_4D'},
        'ferterlizer_usage': {0: np.nan, 1: np.nan, 2: 'NPK', 3: 'NPK50', 4: 'N80', 5: np.nan, 6: np.nan, 7: np.nan},
        'Date_DOP': {0: 10, 1: 20, 2: 15, 3: 25, 4: 35, 5: 11, 6: 22, 7: 33},
        'merged_column': {0: 'NPK', 1: 'NPK50', 2: np.nan, 3: np.nan, 4: np.nan, 5: 'N50P30', 6: 'NPK', 7: 'N50P30'},
    })
    assert_frame_equal(result, expected)


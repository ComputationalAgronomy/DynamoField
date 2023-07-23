import pandas as pd
import pytest
from pandas.testing import assert_frame_equal

from dynamofield.db import dynamodb_server
from dynamofield.field import field_table, importer
from dynamofield.stats import summary_stats


@pytest.fixture
def field_trial():
    table_name = "ft_db"
    dynamodb = dynamodb_server.DynamodbServer()
    field_trial = field_table.FieldTable(dynamodb.dynamodb_res, table_name)
    return field_trial



def test_stats_manual(field_trial: field_table.FieldTable):

    trial_id = "trial_2B"
    df_plots = field_trial.query_df_all_plots(trial_id)
    data = {'trial_id': {0: 'trial_2B', 1: 'trial_2B', 2: 'trial_2B', 3: 'trial_2B', 4: 'trial_2B', 5: 'trial_2B', 6: 'trial_2B', 7: 'trial_2B', 8: 'trial_2B', 9: 'trial_2B', 10: 'trial_2B', 11: 'trial_2B', 12: 'trial_2B', 13: 'trial_2B', 14: 'trial_2B', 15: 'trial_2B', 16: 'trial_2B', 17: 'trial_2B', 18: 'trial_2B', 19: 'trial_2B', 20: 'trial_2B', 21: 'trial_2B', 22: 'trial_2B', 23: 'trial_2B'},
            'info': {0: 'plot_1-1', 1: 'plot_1-2', 2: 'plot_1-3', 3: 'plot_1-4', 4: 'plot_1-5', 5: 'plot_1-6', 6: 'plot_2-1', 7: 'plot_2-2', 8: 'plot_2-3', 9: 'plot_2-4', 10: 'plot_2-5', 11: 'plot_2-6', 12: 'plot_3-1', 13: 'plot_3-2', 14: 'plot_3-3', 15: 'plot_3-4', 16: 'plot_3-5', 17: 'plot_3-6', 18: 'plot_4-1', 19: 'plot_4-2', 20: 'plot_4-3', 21: 'plot_4-4', 22: 'plot_4-5', 23: 'plot_4-6'},
            'treatment': {0: 'T3', 1: 'T1', 2: 'T4', 3: 'T6', 4: 'T3', 5: 'T1', 6: 'T4', 7: 'T5', 8: 'T3', 9: 'T2', 10: 'T1', 11: 'T2', 12: 'T6', 13: 'T6', 14: 'T1', 15: 'T5', 16: 'T2', 17: 'T5', 18: 'T5', 19: 'T3', 20: 'T4', 21: 'T6', 22: 'T4', 23: 'T2'},
            # 'plot': {0: 'plot_1-1', 1: 'plot_1-2', 2: 'plot_1-3', 3: 'plot_1-4', 4: 'plot_1-5', 5: 'plot_1-6', 6: 'plot_2-1', 7: 'plot_2-2', 8: 'plot_2-3', 9: 'plot_2-4', 10: 'plot_2-5', 11: 'plot_2-6', 12: 'plot_3-1', 13: 'plot_3-2', 14: 'plot_3-3', 15: 'plot_3-4', 16: 'plot_3-5', 17: 'plot_3-6', 18: 'plot_4-1', 19: 'plot_4-2', 20: 'plot_4-3', 21: 'plot_4-4', 22: 'plot_4-5', 23: 'plot_4-6'},
            'meta': {0: 9.6, 1: 6.2, 2: 1.2, 3: 9.2, 4: 5.2, 5: 8.2, 6: 4.2, 7: 7.6, 8: 9.3, 9: 5.7, 10: 2.6, 11: 2.0, 12: 2.8, 13: 9.8, 14: 5.9, 15: 8.9, 16: 4.8, 17: 1.3, 18: 6.0, 19: 3.5, 20: 6.5, 21: 4.2, 22: 2.7, 23: 7.5},
            'yields': {0: 51.25, 1: 56.06, 2: 69.76, 3: 96.23, 4: 84.98, 5: 70.02, 6: 78.08, 7: 73.6, 8: 88.33, 9: 96.39, 10: 93.21, 11: 94.05, 12: 82.13, 13: 66.0, 14: 89.26, 15: 65.49, 16: 77.3, 17: 50.01, 18: 52.25, 19: 88.92, 20: 68.19, 21: 98.25, 22: 96.49, 23: 54.32}}
    expected = pd.DataFrame(data)
    assert_frame_equal(df_plots, expected)

    results = df_plots.groupby("treatment").mean(numeric_only=True)
    data = {'meta': {'T1': 5.725, 'T2': 5.0, 'T3': 6.9, 'T4': 3.65, 'T5': 5.95, 'T6': 6.5},
            'yields': {'T1': 77.1375, 'T2': 80.515, 'T3': 78.37, 'T4': 78.13, 'T5': 60.3375, 'T6': 85.6525}}
    expected = pd.DataFrame(data)
    expected.index.name="treatment"
    assert_frame_equal(results, expected)


def test_stats_summary_single(field_trial: field_table.FieldTable):

    trial_id = "trial_2B"
    df_plots = field_trial.query_df_all_plots(trial_id)
    # result = summary_stats.summary_table_df(df_plots, factor="treatment", response="yields")

    results = summary_stats.summary_table_single(df_plots, factor="treatment", response="yields")
    data = {('yields', 'median'): {'T1': 79.64, 'T2': 85.675, 'T3': 86.655, 'T4': 73.92, 'T5': 58.87, 'T6': 89.18},
            ('yields', 'mean'): {'T1': 77.1375, 'T2': 80.515, 'T3': 78.37, 'T4': 78.13, 'T5': 60.3375, 'T6': 85.6525},
            ('yields', 'std'): {'T1': 17.32243319128888, 'T2': 19.42271951435569, 'T3': 18.163063251188287, 'T4': 12.98656485244141, 'T5': 11.172989379153034, 'T6': 14.935520022193183}}
    expected = pd.DataFrame(data)
    expected.index.name = "treatment"
    assert_frame_equal(results, expected)


def test_stats_summary_single_df(field_trial: field_table.FieldTable):

    trial_id = ["trial_2B", "trial_3C"]
    df_plots = field_trial.query_df_all_plots(trial_id)

    results = summary_stats.summary_table_single(df_plots, factor="treatment", response="yields")
    data_both = {('yields', 'median'): {'T1': 80.085, 'T2': 74.19999999999999, 'T3': 76.23, 'T4': 75.64, 'T5': 67.4, 'T6': 81.29499999999999},
                 ('yields', 'mean'): {'T1': 76.7725, 'T2': 71.855, 'T3': 74.17875000000001, 'T4': 77.82124999999999, 'T5': 65.3775, 'T6': 81.97},
                 ('yields', 'std'): {'T1': 12.617986878149098, 'T2': 18.04422424410173, 'T3': 15.438926163157479, 'T4': 13.471040300797643, 'T5': 13.462920241484438, 'T6': 12.826546133479809}}
    expected = pd.DataFrame(data_both)
    expected.index.name = "treatment"
    assert_frame_equal(results, expected)

    results = summary_stats.summary_table_df(df_plots, factor="treatment", response="yields")
    assert_frame_equal(results["All"], expected)


def test_stats_summary_multi(field_trial: field_table.FieldTable):

    trial_id = ["trial_2B", "trial_3C"]
    df_plots = field_trial.query_df_all_plots(trial_id)
    # results = summary_stats.summary_table_single(df_plots, factor="treatment", response="yields")
    # data_both = {('yields', 'median'): {'T1': 80.085, 'T2': 74.19999999999999, 'T3': 76.23, 'T4': 75.64, 'T5': 67.4, 'T6': 81.29499999999999},
    #              ('yields', 'mean'): {'T1': 76.7725, 'T2': 71.855, 'T3': 74.17875000000001, 'T4': 77.82124999999999, 'T5': 65.3775, 'T6': 81.97},
    #              ('yields', 'std'): {'T1': 12.617986878149098, 'T2': 18.04422424410173, 'T3': 15.438926163157479, 'T4': 13.471040300797643, 'T5': 13.462920241484438, 'T6': 12.826546133479809}}
    # expected = pd.DataFrame(data_both)
    # expected.index.name="treatment"
    # assert_frame_equal(results, expected)

    results = summary_stats.summary_table_df(df_plots, factor="treatment", response="yields", by="trial_id")

    # assert_frame_equal(results, expected)
    data2 = {('yields', 'median'): {'T1': 79.64, 'T2': 85.675, 'T3': 86.655, 'T4': 73.92, 'T5': 58.87, 'T6': 89.18},
             ('yields', 'mean'): {'T1': 77.1375, 'T2': 80.515, 'T3': 78.37, 'T4': 78.13, 'T5': 60.3375, 'T6': 85.6525},
             ('yields', 'std'): {'T1': 17.32243319128888, 'T2': 19.42271951435569, 'T3': 18.163063251188287, 'T4': 12.98656485244141, 'T5': 11.172989379153034, 'T6': 14.935520022193183}}
    data3 = {('yields', 'median'): {'T1': 80.085, 'T2': 61.5, 'T3': 66.66, 'T4': 77.545, 'T5': 72.67500000000001, 'T6': 77.13999999999999},
             ('yields', 'mean'): {'T1': 76.4075, 'T2': 63.195, 'T3': 69.9875, 'T4': 77.5125, 'T5': 70.4175, 'T6': 78.2875},
             ('yields', 'std'): {'T1': 8.430683542868868, 'T2': 13.508852652982783, 'T3': 13.395271242743343, 'T4': 15.953758961448552, 'T5': 15.177084425760658, 'T6': 11.164620832492854}}
    expected = pd.DataFrame(data2)
    expected.index.name = "treatment"
    assert_frame_equal(results["trial_2B"], expected)
    expected = pd.DataFrame(data3)
    expected.index.name = "treatment"
    assert_frame_equal(results["trial_3C"], expected)



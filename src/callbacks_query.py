import datetime
import io
import os

import dash
import dash_bootstrap_components as dbc
import numpy as np
import pandas as pd
import plotly.express as px
from dash import Dash, ctx, dash_table, dcc, html
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate

import app_style
import app_data
from dynamofield.db import dynamodb_init, init_db, key_utils, table_utils
from dynamofield.df import df_operation
from dynamofield.field import field_table, importer
from dynamofield.stats import summary_stats
from dynamofield.utils import json_utils




@dash.callback(
    Output('select_trial', 'options'),
    Output('select_trial', 'disabled'),
    Input('tabs-function', 'value'),
    State('store_db_info', 'data'),
)
def get_id_list(tab, db_info):
    if tab != "tab-query" or db_info is None:
        raise PreventUpdate
    if not db_info["db_status"] or not db_info["table_status"]:
        print("Database offline")
        ids = [False]
        is_disabled = True
    else:
        # field_trial = init_field_trial(db_info["endpoint"], db_info["table_name"])
        field_trial = app_data.connect_db_table(db_info)
        ids = field_trial.get_all_trial_id()
        is_disabled = False
        # field_trial = init_field_trial(endpoint, table_name)
        # data = field_trial.get_by_trial_ids(trial_id, info_list)
    print(f"{ids}")
    return ids, is_disabled


@dash.callback(
    Output('dropdown_info_sortkey', 'options'),
    Input('select_trial', 'value'),
    State('store_db_info', 'data'),
)
def update_output_info(trial_ids, db_info):
    if not trial_ids:
        return []
    # if value is not None:
    field_trial = app_data.connect_db_table(db_info)
    info_global = set()
    for trial in trial_ids:
        info = field_trial.list_all_sort_keys(trial)
        info_set = key_utils.extract_sort_key_prefix(info)
        info_global.update(info_set)
        # print(info_global)
    info_global = list(info_global)
    info_global.sort()
    return info_global  # , info_global, info_global


@dash.callback(
    Output('dropdown_info_sortkey', 'value'),
    Input('button_info_all', 'n_clicks'),
    Input('button_info_none', 'n_clicks'),
    State('dropdown_info_sortkey', 'options'),
)
def update_info_selection_btn(b1, b2, options):
    if not options:
        raise PreventUpdate
    if "button_info_all" == ctx.triggered_id:
        return options
    elif "button_info_none" == ctx.triggered_id:
        return None


@dash.callback(
    Output("data_table", "data"),
    Input("store_data_table", "data"),
)
def update_output_table(store_table):
    return store_table


# @dash.callback(
#     # Output("data_table", "columns"),
#     # Output("data_table", "data"),
#     # Output("store_data_table", "data"),
#     # Output('dropdown_info_merge_column', 'options'),
#     # Output('dropdown_info_sortkey_t1', 'options'),
#     # Output('dropdown_info_sortkey_t2', 'options'),
#     # Output("dropdown_xaxis", "options"),
#     # Output("dropdown_yaxis", "options"),
#     # Output("dropdown_by", "options"),
#     # Output("data_info", "children"),
#     Input("btn_merge_column", "n_clicks"),
#     State('select_trial', 'value'),
#     State('dropdown_info_sortkey', 'value'),
#     State('dropdown_info_sortkey', 'options'),
#     State('dropdown_info_merge', 'value'),
#     State("dropdown_info_merge_columns", "value"),
#     State("store_data_table", "data"),
#     State('store_db_info', 'data'),
# )
# def merge_columns_within_info(b_merge_column,
#                               trial_id, info_list, info_options,
#                               info_merge, merge_columns,
#                               data_table, db_info):
#     if not trial_id or not db_info["db_status"] or not db_info["table_status"]:
#         raise PreventUpdate
#     print(f"trial_id:{trial_id}")
#     # if "btn_fetch_data" == ctx.triggered_id:
#     #     print(f"info_list:{info_list}\t{info_options}")
#     #     if info_list is None:
#     #         info_list = info_options
#     field_trial = app_data.connect_db_table(db_info)
#     data = field_trial.query_by_trial_ids(trial_id, info_merge)
#     data = pd.read_csv("tests/test_data/test_plot.csv")
#     data = data.loc[0:15, ]
#     # df_output = json_utils.result_list_to_df(data)
#     data.loc[0:5, merge_columns[0:2]] = None
#     data.loc[6:10, merge_columns[1:3]] = None
#     data.iloc[11:16, [1,3]] = None

#     # check each row only has one value
#     data_sub.apply(pd.isnull, axis=1)
#     is_single_list = data_sub.apply(check_single_value_per_row, axis=1)
#     is_mergable = all(is_single_list)
#     if is_mergable:
#         data_sub = data_sub.apply(lambda x: x.dropna().iat[0], axis=1)


@dash.callback(
    # Output("data_table", "columns"),
    # Output("data_table", "data"),
    Output("store_data_table", "data"),
    Output('dropdown_info_merge', 'options'),
    Output('dropdown_info_sortkey_t1', 'options'),
    Output('dropdown_info_sortkey_t2', 'options'),
    Output("dropdown_xaxis", "options"),
    Output("dropdown_yaxis", "options"),
    Output("dropdown_by", "options"),
    Output("data_info", "children"),
    Input("btn_fetch_data", "n_clicks"),
    Input("btn_merge_info_tables", "n_clicks"),
    Input("btn_merge_columns", "n_clicks"),
    State('select_trial', 'value'),
    State('dropdown_info_sortkey', 'value'),
    State('dropdown_info_sortkey', 'options'),
    State('dropdown_info_sortkey_t1', 'value'),
    State('dropdown_info_sortkey_t2', 'value'),
    State("dropdown_info_t1_column", "value"),
    State("dropdown_info_t2_column", "value"),
    State('dropdown_info_merge', 'value'),
    State("dropdown_info_merge_columns", "value"),
    State("store_data_table", "data"),
    State('store_db_info', 'data'),

)
def update_data_table(b_fetch, b_merge_info, btn_merge_column,
                      trial_id, info_list, info_options,
                      info_t1, info_t2, t1_column, t2_column,
                      info_merge, merge_columns,
                      data_table, db_info):
    if not trial_id or not db_info["db_status"] or not db_info["table_status"]:
        raise PreventUpdate
    df_output = pd.DataFrame()
    print(f"trial_id:{trial_id}\t Trigger:{ctx.triggered_id}")
    if "btn_fetch_data" == ctx.triggered_id:
        print(f"info_list:{info_list}\t{info_options}")
        if info_list is None:
            info_list = info_options
        field_trial = app_data.connect_db_table(db_info)
        data = field_trial.query_by_trial_ids(trial_id, info_list)
        df_output = json_utils.result_list_to_df(data)
    elif ("btn_merge_info_tables" == ctx.triggered_id and
          data_table and t1_column and t2_column):
        print(f"column_select:{t1_column}\t{t2_column}")
        dd = pd.DataFrame(data_table)
        info_list = [info_t1, info_t2]
        df_output = df_operation.merge_df(dd, info_t1, info_t2,
                                          t1_column, t2_column)
    elif ("btn_merge_columns" == ctx.triggered_id and data_table and
          info_merge and merge_columns):
        # dd = pd.DataFrame(data_table)
        print(f"merge_columns:{merge_columns}\tat_info:{info_merge}")
        field_trial = app_data.connect_db_table(db_info)
        data_temp = field_trial.query_by_trial_ids(trial_id, info_merge)
        data = json_utils.result_list_to_df(data_temp)
        df_output = df_operation.merge_multi_columns(data, merge_columns)

    data_info = f"Data: {df_output.shape[0]} rows, {df_output.shape[1]} columns."
    output = [df_output.to_dict('records'),
              info_list, info_list, info_list,
              df_output.columns, df_output.columns, df_output.columns,
              data_info]
    return output


@dash.callback(
    Output("dropdown_info_t1_column", "options"),
    Output("dropdown_info_t2_column", "options"),
    Input('dropdown_info_sortkey_t1', 'value'),
    Input('dropdown_info_sortkey_t2', 'value'),
    State("data_table", "columns"),
    State("store_data_table", "data"),
)
def update_select_two_tables(info_1, info_2, columns, data_table):
    if not info_1 or not info_2:
        raise PreventUpdate
    # t1_c = None
    # t2_c = None
    print(f"info:{info_1}\t{info_2}")
    dd = pd.DataFrame(data_table)
    t1_c = df_operation.get_non_na_column_name(dd, info_1)
    t2_c = df_operation.get_non_na_column_name(dd, info_2)

    return t1_c, t2_c


@dash.callback(
    Output("dropdown_info_merge_columns", "options"),
    Input('dropdown_info_merge', 'value'),
    State("data_table", "columns"),
    State("store_data_table", "data"),
)
def update_select_info_column_names(info, columns, data_table):
    if not info:
        raise PreventUpdate
    dd = pd.DataFrame(data_table)
    cc = df_operation.get_non_na_column_name(dd, info)
    return cc


@dash.callback(
    Output("export_data", "data"),
    Input("btn_export", "n_clicks"),
    State("data_table", "data"),
    prevent_initial_call=True,
)
def export_dataframe(n_clicks, df):
    if not df:
        raise PreventUpdate
    df2 = pd.DataFrame(df)
    #  df.to_csv('df.csv', index=False, encoding='utf-8')
    # datetime
    return dcc.send_data_frame(df2.to_csv, filename="hello.csv")


@dash.callback(
    Output('data_figure', 'figure'),
    Input('btn_plot', 'n_clicks'),
    State("store_data_table", "data"),
    State('dropdown_xaxis', 'value'),
    State('dropdown_yaxis', 'value'),
    State('dropdown_by', 'value'),
    State("raido-plot-type", "value"),
    prevent_initial_call=True,
)
def update_figure(n_clicks, data_table, var_x, var_y, var_by, plot_type):
    # filtered_df = df[df.year == selected_year]
    if not var_x and not var_y:
        raise PreventUpdate
    df = pd.DataFrame(data_table)
    if plot_type == "Bar":
        fig = px.bar(df, x=var_x, y=var_y, color=var_by)
    elif plot_type == "Line":
        fig = px.line(df, x=var_x, y=var_y, color=var_by)
    elif plot_type == "Scatter":
        fig = px.scatter(df, x=var_x, y=var_y, color=var_by)

    fig.update_layout(transition_duration=500)

    return fig


@dash.callback(
    Output("stats_output", "children"),
    Input('btn_stats', 'n_clicks'),
    Input('btn_summary', 'n_clicks'),
    State("store_data_table", "data"),
    State('dropdown_xaxis', 'value'),
    State('dropdown_yaxis', 'value'),
    State('dropdown_by', 'value'),
    prevent_initial_call=True,
)
def stat_analysis(btn_stat, btn_summary, data_table,
                  var_x, var_y, var_by):
    if not var_x and not var_y:
        raise PreventUpdate
    df = pd.DataFrame(data_table)
    print(f"stats:{df.shape}\t{df.columns}\tVar:{var_x}, {var_y}, {var_by}")
    if "btn_stats" == ctx.triggered_id:
        results = summary_stats.analysis_design(
            df, factor=var_x, response=var_y, by=var_by)
    elif "btn_summary" == ctx.triggered_id:
        results = summary_stats.summary_table_df(
            df, factor=var_x, response=var_y, by=var_by)
    out = [f"Dataset:{k}\n{v}\n\n" for k, v in results.items()]
    output = "".join(out)
    stats_output = f"{output}"
    return stats_output

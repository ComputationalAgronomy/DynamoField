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
from app_data import *
from dynamofield.db import dynamodb_init, init_db, key_utils, table_utils
from dynamofield.df import df_operation
from dynamofield.field import field_table, importer
from dynamofield.utils import json_utils


def trial_selection_panel():
    return html.Div(style={'padding': 10},
                    children=[
        dbc.Row([
            dbc.Col([
                dbc.Label('Select trial ID'),
                dcc.Dropdown(multi=True, id="select_trial"),
            ], width=3),
            dbc.Col([
                dbc.Label('Multi-Select Information related to this trial'),
                dcc.Dropdown(id="dropdown_info_sortkey", multi=True),
                dbc.Button('Select All', id='button_info_all', n_clicks=0,
                           size="lg", className="my-2"), #style=app_style.btn_style),
                dbc.Button('Select None', id='button_info_none', n_clicks=0,
                           size="lg", className="m-2", 
                           #style={"margin-left": "5px", "margin-top": "5px"}
                           ),
            ], width={"size": 3, "offset": 0.5}),
            dbc.Col([
                html.Br(),
                dbc.Button('Fetch data', id='bt_fetch_data', size="lg",
                           n_clicks=0, 
                           className="m-2",
                           style={# "margin":"10px", 'margin-top': '20px', 
                                "width":"200px", "height":"60px", 
                                'align-items': 'center', 'justify-content': 'center'
                           }),
            ], width={"size": "auto", "offset": 1}),
        ]),
        dcc.Markdown(id="data_info"), 
    ])


def merging_two_info():
    return html.Div(style={'padding': 10},
                    children=[
        dbc.Row(html.H6("Merging info tables")),
        dbc.Row([
            dbc.Col([
                dbc.Label('First info table'),
                dcc.Dropdown(id="dropdown_info_sortkey_t1", multi=False),
                dbc.Label('First table - Column name'),
                dcc.Dropdown(id="dropdown_info_t1_column", multi=False),
            ], width={"size": 3}),
            dbc.Col([
                dbc.Label('Second info table'),
                dcc.Dropdown(id="dropdown_info_sortkey_t2", multi=False),
                dbc.Label('Second table - Column name'),
                dcc.Dropdown(id="dropdown_info_t2_column", multi=False),
            ], width={"size": 3, "offset": 0.5}),
            dbc.Col([
                html.Br(),
                dbc.Button('Merge table', id='bt_merge_info_tables',
                           n_clicks=0, size="lg",
                           className="m-2",
                           style={  # "margin":"10px", 'margin-top': '20px',
                               "width": "200px", "height": "60px",
                               'align-items': 'center', 'justify-content': 'center'
                           }),
            ], width={"size": "auto", "offset": 1})
        ]),


    ])

def plotting_panel():
    return html.Div(style={'padding': 10}, 
                    children=[
        dbc.Row(html.H6("Plotting data.")),
        dbc.Row([
            dbc.Col([
                dcc.Markdown("**X-axis**"),
                dcc.Dropdown(id="dropdown_xaxis", multi=False),
            ], width=3),
            dbc.Col([
                dcc.Markdown("**Y-axis**"),
                dcc.Dropdown(id="dropdown_yaxis", multi=False),
            ], width=3),
            dbc.Col([
                dcc.Markdown("\[Optional\] Colour"),
                dcc.Dropdown(id="dropdown_colour", multi=False, disabled=True),
            ], width=2),
            dbc.Col([
                dbc.Label("Plot type:"),
                dcc.RadioItems(options=["Scatter", "Line", "Bar"], 
                    value = "Scatter", 
                    id="raido-plot-type", 
                    style={"display": "flex", "margin": 5}
                ),
            ], width=2),
            dbc.Col([
                html.Br(),
                dbc.Button("Plot data", id="btn_plot",
                           className="m-2",
                           style={# "margin":"10px", 'margin-top': '20px', 
                                "width":"200px", "height":"60px", 
                                'align-items': 'center', 'justify-content': 'center'
                           }),
            ], width=2),
        ], ),

    ])

def generate_query_panel():
    return [html.Div(id="query_panel", 
                     style={'padding': 10},
                     children=[
        dcc.Store(id='store_data_table', storage_type='session', clear_data=True),
        trial_selection_panel(),
        html.Hr(style={"height":"2px", "margin":"5px"}),
        
        merging_two_info(),
        plotting_panel(),
        html.Hr(style={"height":"2px", "margin":"5px"}),
        
        
        html.H5("Table"),
        # html.Br(),
        # dbc.Button("Export data table (CSV)",
        #             id="btn_export",
        #             style=app_style.btn_style),
        # dcc.Download(id="export_data"),
        # html.Br(),
        dash_table.DataTable(id="data_table",
                            page_size=50,  # we have less data in this example, so setting to 20
                            style_table={
                                'height': '300px', 'overflowY': 'auto'},
                            export_format='csv'),
        dcc.Graph(id='data_figure'),
    ])]



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
        print(f"Database offline")
        ids = [False]
        is_disabled = True
    else:
        # field_trial = init_field_trial(db_info["endpoint"], db_info["table_name"])
        field_trial = connect_db_table(db_info)
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
    field_trial = connect_db_table(db_info)
    info_global = set()
    for trial in trial_ids:
        info = field_trial.list_all_sort_keys(trial)
        info_set = key_utils.extract_sort_key_prefix(info)
        info_global.update(info_set)
        # print(info_global)
    info_global = list(info_global)
    info_global.sort()
    return info_global # , info_global, info_global


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
    


@dash.callback(
    # Output("data_table", "columns"), 
    # Output("data_table", "data"),
    Output("store_data_table", "data"),
    Output('dropdown_info_sortkey_t1', 'options'),
    Output('dropdown_info_sortkey_t2', 'options'),
    Output("dropdown_xaxis", "options"), 
    Output("dropdown_yaxis", "options"),
    Output("dropdown_colour", "options"),
    Output("data_info", "children"),
    Input("bt_fetch_data", "n_clicks"),
    Input("bt_merge_info_tables", "n_clicks"),
    State('select_trial', 'value'),
    State('dropdown_info_sortkey', 'value'),
    State('dropdown_info_sortkey', 'options'),
    State('dropdown_info_sortkey_t1', 'value'),
    State('dropdown_info_sortkey_t2', 'value'),
    State("dropdown_info_t1_column", "value"),
    State("dropdown_info_t2_column", "value"),
    State("store_data_table", "data"),
    State('store_db_info', 'data'),
    
)
def update_data_table(b_fetch, b_merge,
                      trial_id, info_list, info_options,
                      info_t1, info_t2, t1_column, t2_column,
                      data_table, db_info):
    if not trial_id or not db_info["db_status"] or not db_info["table_status"]:
        raise PreventUpdate
    print(f"trial_id:{trial_id}")
    if "bt_fetch_data" == ctx.triggered_id:
        print(f"info_list:{info_list}\t{info_options}")
        if info_list is None:
            info_list = info_options
        field_trial = connect_db_table(db_info)
        data = field_trial.query_by_trial_ids(trial_id, info_list)
        df = json_utils.result_list_to_df(data)
        # print(df)
        columns = [{"name": i, "id": i} for i in df.columns]
        data_info = f"Data: {df.shape[0]} rows, {df.shape[1]} columns."
        output = [df.to_dict('records'),
                  info_list, info_list,
                  df.columns, df.columns, df.columns,
                  data_info]
        return output
    if "bt_merge_info_tables" == ctx.triggered_id and data_table and t1_column and t2_column:
        print(f"column_select:{t1_column}\t{t2_column}")
        dd = pd.DataFrame(data_table)
        info_list = [info_t1, info_t2]
        df_merge = df_operation.merge_df(dd, info_t1, info_t2, 
                                         t1_column, t2_column)
        output = [df_merge.to_dict('records'),
                  info_list, info_list,
                  df_merge.columns, df_merge.columns, df_merge.columns,
                  "data_info"]
        return output



@dash.callback(
    Output("dropdown_info_t1_column", "options"),
    Output("dropdown_info_t2_column", "options"),
    Input('dropdown_info_sortkey_t1', 'value'),
    Input('dropdown_info_sortkey_t2', 'value'),
    State("data_table", "columns"), 
    State("data_table", "data"),
)
def update_select_two_tables(info_1, info_2, columns, data_table):
    if not info_1 or not info_2:
        raise PreventUpdate
    t1_c = None
    t2_c = None
    print(f"info:{info_1}\t{info_2}")
    dd = pd.DataFrame(data_table)
    t1_c = df_operation.get_non_na_column_name(dd, info_1)
    t2_c = df_operation.get_non_na_column_name(dd, info_2)

    return t1_c, t2_c





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
    State("data_table", "data"),
    State('dropdown_xaxis', 'value'), 
    State('dropdown_yaxis', 'value'),
    # State('dropdown_colour', 'value'),
    State("raido-plot-type", "value"),
    prevent_initial_call=True,
)
def update_figure(n_clicks, df, var_x, var_y, var_col, plot_type):
    # filtered_df = df[df.year == selected_year]
    if not var_x and not var_y:
        raise PreventUpdate
    df2 = pd.DataFrame(df)
    if plot_type == "Bar":
        fig = px.bar(df2, x=var_x, y=var_y)  # , color=var_col)
    elif plot_type == "Line":
        fig = px.line(df2, x=var_x, y=var_y)  # , color=var_col)
    elif plot_type == "Scatter":
        fig = px.scatter(df2, x=var_x, y=var_y)  # , color=var_col)

    fig.update_layout(transition_duration=500)

    return fig

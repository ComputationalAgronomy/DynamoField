
import dash
import numpy as np
import pandas as pd
from dash import Dash, ctx, dash_table, dcc, html
from dash.dependencies import ClientsideFunction, Input, Output, State
from dash.exceptions import PreventUpdate

from app_data import *


@dash.callback(
    Output('get_item_count', 'children'),
    Input('tabs-function', 'value')
)
def update_item_count_import(x):
    return update_item_count()


@dash.callback(
    Output('get_item_count_db', 'children'),
    Input('tabs-function', 'value')
)
def update_item_count_db(x):
    return update_item_count()



@dash.callback(
    Output('data_endpoint', 'children'),
    Output('data_tablename', 'children'),
    # Output("loading_update_db", "children"),
    # Output('store_endpoint', 'data'),
    # Output('store_table_name', 'data'),
    # Input('btn_endpoint', 'n_clicks'),
    Input("refresh-graph-interval", "n_intervals"),
    State('store_endpoint', 'data'),
    State('store_tablename', 'data'),
)
def get_memory_data(x, endpoint, tablename):
    print("memory:", endpoint, tablename, x)
    return endpoint, tablename





@dash.callback(
    Output('db_endpoint', 'value'),
    Output('db_tablename', 'value'),
    Output('store_endpoint', 'data'),
    Output('store_tablename', 'data'),
    Output('store_db_status', 'data'),
    Output('store_table_status', 'data'),
    Output("loading_update_db", "children"),
    Input('btn_endpoint', 'n_clicks'),
    State('db_endpoint', 'value'),
    State('db_tablename', 'value'),
    State('store_endpoint', 'data'),
    State('store_tablename', 'data'),
    running=[
        (Output("btn_endpoint", "disabled"), True, False),
    ],
)
def update_db_status(btn, ep, name, m_ep, m_name):
    # if not ep:
    #     raise PreventUpdate
    # update_endpoint
    print(f"Start: ={ep}= ={name}=\t\tmemory: {m_ep} {m_name}")
    if ep == m_ep and name == m_name:
        raise PreventUpdate

    endpoint = None
    tablename = None
    if ep:
        endpoint = ep
    elif m_ep:
        endpoint = m_ep

    if name:
        tablename = name
    elif m_name:
        tablename = m_name
    # if not ep and not name:
    #     endpoint = "http://localhost:8000"
    #     tablename = "ft_db"
    print(f"update: {endpoint} {tablename}")
    if not endpoint or not tablename:
        raise PreventUpdate

    # if ep is None and m_ep:
    dynamodb_server = init_dynamodb(endpoint)
    # dynamodb_server.is_dynamodb_online()
    db_status = dynamodb_server.is_online
    table_status = False
    if db_status:
        table_status = dynamodb_server.is_table_exist(tablename)
    print("Status:\t", db_status, table_status)
    # field_trial = init_field_trial(
    #     dynamodb_server,
    #     table_name=table_name_default)
    # dynamodb_server.update_endpoint(endpoint)
    # print(f"update: {endpoint} {tablename}")

    return endpoint, tablename, endpoint, tablename, db_status, table_status, True




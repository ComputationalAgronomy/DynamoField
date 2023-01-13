
import dash
import numpy as np
import pandas as pd
from dash import Dash, ctx, dash_table, dcc, html
from dash.dependencies import ClientsideFunction, Input, Output, State
from dash.exceptions import PreventUpdate

from app_data import *


@dash.callback(
    Output('get_item_count', 'children'),
    Input('tabs-function', 'value'),
        State('store_endpoint', 'data'),
    State('store_table_name', 'data'),

)
def update_item_count_import(x, endpoint, table_name):
    return update_item_count()


@dash.callback(
    Output('get_item_count_db', 'children'),
    Input('tabs-function', 'value'),
        State('store_endpoint', 'data'),
    State('store_table_name', 'data'),

)
def update_item_count_db(x, endpoint, table_name):
    return update_item_count()



@dash.callback(
    Output('data_endpoint', 'children'),
    Output('data_table_name', 'children'),
    Output('data_db_status', 'children'),
    Output('data_table_status', 'children'),
    # Output('store_db_info', 'data'),
    Input("refresh-graph-interval", "n_intervals"),
    State('store_endpoint', 'data'),
    State('store_table_name', 'data'),
    State('store_db_status', 'data'),
    State('store_table_status', 'data'),
    State('store_db_info', 'data'),
)
def get_memory_data(x, endpoint, table_name, db_status, table_status, info):
    print("memory:", endpoint, table_name, db_status, table_status, x)
    # info = {
    #     "endpoint": endpoint,
    #     "table_name": table_name,
    #     "db_status":db_status,
    #     "table_status": table_status,
    #     endpoint: db_status,
    #     table_name: table_status
    # }
    for k, v in info.items():
        print("\t", k, v)
    return endpoint, table_name, str(db_status), str(table_status)





@dash.callback(
    Output('db_endpoint', 'value'),
    Output('db_table_name', 'value'),
    Output('store_endpoint', 'data'),
    Output('store_table_name', 'data'),
    Output('store_db_status', 'data'),
    Output('store_table_status', 'data'),
    Output("loading_update_db", "children"),
    Output('store_db_info', 'data'),
    Input('btn_connect_db', 'n_clicks'),
    State('db_endpoint', 'value'),
    State('db_table_name', 'value'),
    State('store_endpoint', 'data'),
    State('store_table_name', 'data'),
    running=[
        (Output("btn_connect_db", "disabled"), True, False),
    ],
)
def update_db_status(btn, ep, name, m_ep, m_name):
    # if not ep:
    #     raise PreventUpdate
    # update_endpoint
    print(f"Start: ={ep}=={name}=\tmemory:{m_ep}=={m_name}=")
    if ep == m_ep and name == m_name:
        print("No update")
        raise PreventUpdate

    endpoint = None
    table_name = None
    if ep:
        endpoint = ep
    elif m_ep:
        endpoint = m_ep

    if name:
        table_name = name
    elif m_name:
        table_name = m_name
    # if not ep and not name:
    #     endpoint = "http://localhost:8000"
    #     table_name = "ft_db"
    print(f"Update: {endpoint} {table_name}")
    if not endpoint or not table_name:
        raise PreventUpdate

    # if ep is None and m_ep:
    dynamodb_server = init_dynamodb(endpoint)
    # dynamodb_server.is_dynamodb_online()
    db_status = dynamodb_server.is_online
    table_status = False
    if db_status:
        table_status = dynamodb_server.is_table_exist(table_name)
    print("Status:\t", db_status, table_status)
    # field_trial = init_field_trial(
    #     dynamodb_server,
    #     table_name=table_name_default)
    # dynamodb_server.update_endpoint(endpoint)
    # print(f"update: {endpoint} {table_name}")
    info = {
        "endpoint": endpoint,
        "table_name": table_name,
        "db_status":db_status,
        "table_status": table_status,
        endpoint: db_status,
        table_name: table_status
    }
    return endpoint, table_name, endpoint, table_name, db_status, table_status, True, info





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
    State('store_db_info', 'data'),
)
def update_item_count_import(x, info):
    return update_item_count(info)


# @dash.callback(
#     Output('get_item_count_db', 'children'),
#     Input('tabs-function', 'value'),
#     State('store_db_info', 'data'),
# )
# def update_item_count_db(x, info):
#     return update_item_count(info)


@dash.callback(
    Output('db_table_md', 'children'),
    Output("dt_list_table", "columns"), 
    Output("dt_list_table", "data"),
    Input('btn_create_table', 'n_clicks'),
    Input('btn_list_tables', 'n_clicks'),
    State('store_db_info', 'data'),
    State('new_table_name', 'value'),
)
def add_new_table(btn_create, btn_list, db_info, tablename):
    print("Table info:", tablename, db_info, dash.callback_context.triggered_id)
    if not db_info["db_status"]:
        raise PreventUpdate
    md = "" # "Database offline."
    columns = None
    data = None
    list_tables = db_list_table(db_info)    
    if dash.callback_context.triggered_id == 'btn_create_table':        
        # if tablename is None or len(tablename) == 0:
        #     md = "Please enter a name for the new table (min length > 3)."
        #     print(md)
        #     raise PreventUpdate
        # # TODO: Check table not already exist
        try:
            md = create_new_table(db_info, tablename)
        except Exception as e:
            md = f"Please enter a name for the new table (min length > 3).<br>{e}"
        
    elif dash.callback_context.triggered_id == 'btn_list_tables':
        # md = f"List of available tables:\n<br>"
        # md = "" #+= "<br> - ".join([t.name for t in list_tables])
        data = [{"table_name": t.name} for t in list_tables]
        table_names = [t.name for t in list_tables]
        columns = [{"name": "Table name", "id": "table_name"}]
    return md, columns, data



# @dash.callback(
#     Output("dt_list_table", "columns"), 
#     Output("dt_list_table", "data"),

#     State('store_db_info', 'data'),
#     prevent_initial_call=True,
# )
# def update_list_table(btn_list, db_info):
#     print(db_info, dash.callback_context.triggered_id)
#     columns = None
#     data = None
#     if db_info["db_status"]:
      





def check_status(status):
    if status:
        colour = "green"
        status_text = "ONLINE"
    else:
        colour = "red"
        status_text = "OFFLINE"
    status_html = status_template_text(colour, status_text)
    return status_html


def status_template_text(colour, text):
    status_html = f"""<b><span style="color: {colour}">{text}</span></b>"""
    return status_html




@dash.callback(
    Output("db_markdown", "children"),
    Input("refresh-graph-interval", "n_intervals"),
    Input('store_db_info', 'data'),
)
def update_status_interval(n, db_info):
    if db_info is None:
        raise PreventUpdate
    try:
        md_db = check_status(db_info["db_status"])
        md_table = check_status(db_info["table_status"])
    except TypeError:
        md_db = check_status(False)
        md_table = check_status(False)
    md_output = f"""<p style="margin: 0;font-size:20pt">
    Database status: {md_db}
    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
    Table status: {md_table}
    </p>"""

    return md_output





@dash.callback(
    Output('data_endpoint', 'children'),
    Output('data_table_name', 'children'),
    Output('data_db_status', 'children'),
    Output('data_table_status', 'children'),
    Input("refresh-graph-interval", "n_intervals"),
    State('store_db_info', 'data'),
)
def get_memory_data(x, db_info):
    if db_info is not None:
        print(f"memory: {db_info}")
        # print("memory:", db_info["endpoint"], db_info["table_name"], db_info["db_status"], db_info["table_status"], x)
        # for k, v in db_info.items():
        #     print("\t", k, v)
        return db_info["endpoint"], db_info["table_name"], str(db_info["db_status"]), str(db_info["table_status"])
    return False, False, False, False




@dash.callback(
    Output('db_endpoint', 'value'),
    Output('db_table_name', 'value'),
    # Output('store_endpoint', 'data'),
    # Output('store_table_name', 'data'),
    # Output('store_db_status', 'data'),
    # Output('store_table_status', 'data'),
    Output('store_db_info', 'data'),
    Output("loading_update_db", "children"),   
    Input('btn_connect_db', 'n_clicks'),
    State('db_endpoint', 'value'),
    State('db_table_name', 'value'),
    State('store_db_info', 'data'),
    # State('store_endpoint', 'data'),
    # State('store_table_name', 'data'),
    running=[
        (Output("btn_connect_db", "disabled"), True, False),
    ],
)
def update_db_status(btn, ep, name, info): #m_ep, m_name):
    # if not ep:
    #     raise PreventUpdate
    # update_endpoint
    # if info is None:
    #     print(f"No update: info:{info}")
    #     raise PreventUpdate
    try:
        m_ep = info["endpoint"]
        m_name = info["table_name"]
    except Exception:
        m_ep = None
        m_name = None
    print(f"Current status: ={ep}=={name}=\tmemory:{m_ep}=={m_name}==\t=={info}")
    if ep == m_ep and name == m_name:
        print("No update")
        raise PreventUpdate

    endpoint = None
    table_name = None
    db_status = False
    table_status = False
    if ep:
        endpoint = ep
    elif m_ep:
        endpoint = m_ep

    if name:
        table_name = name
    elif m_name:
        table_name = m_name

    print(f"Update: {endpoint} {table_name}")
    if endpoint is not None:
        # raise PreventUpdate

        # if ep is None and m_ep:
        dynamodb_server = init_dynamodb(endpoint)
        # dynamodb_server.is_dynamodb_online()
        db_status = dynamodb_server.is_online
    if db_status and table_name is not None:
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
    return endpoint, table_name, info, True




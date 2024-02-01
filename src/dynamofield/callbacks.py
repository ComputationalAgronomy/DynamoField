
import dash
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate

# from app_db import *
from dynamofield.callbacks_db_status import *
from dynamofield.callbacks_query import *


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




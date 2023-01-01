

import base64
import datetime
import io
import os
from datetime import datetime as dt

import dash
import numpy as np
import pandas as pd
from dash import Dash, ctx, dash_table, dcc, html
from dash.dependencies import ClientsideFunction, Input, Output, State
from dash.exceptions import PreventUpdate

from dynamofield.db import dynamodb_init, init_db, key_utils, table_utils
from dynamofield.field import field_table, importer
from dynamofield.utils import json_utils

from app_data import field_trial
# from callbacks import *
import app_style

# item_counts = field_trial.get_item_count()


def generate_db_status_panel():
    return [
        html.Div(style={'padding': 10, 'flex': 1},
                 children=[
            html.Br(),
            html.Div("aoeuaoeu"),
            html.Div(id="get_item_count_db"),
            html.Br(),
            # html.Div(id="get_item_count"),
            dcc.RadioItems(['New York City', 'Montréal',
                            'San Francisco'], 'Montréal'),
            # html.Div(f"Total item count: {item_counts}", id="nths"),
            dcc.RadioItems(['New York City', 'Montréal',
                            'San Francisco'], 'Montréal'),
            # dcc.textinput(value="endpoint_url='http://localhost:8000')"),
            html.Button('Start database', id='btn_db_start',
                        n_clicks=0,  # style=app_style.btn_style,
                        className="two columns"
                        ),

        ],),
    ]


# @dash.callback(
#     Output('get_item_count', 'children'),
#     Input('tabs-function', 'value')
# )
# def update_item_count(x):
#     # if not value:
#     #     raise PreventUpdate
#     # # if value is not No?ne:
#     # info = field_trial.list_all_sort_keys(value)
#     # info_global = key_utils.extract_sort_key_prefix(info)
#     # print(info_global[0])
#     item_counts = field_trial.get_item_count()
#     return f"Total item count: {item_counts}"

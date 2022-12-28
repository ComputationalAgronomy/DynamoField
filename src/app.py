# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.


import datetime
# import field
import importlib
import os
from datetime import datetime as dt
import base64
import datetime
import io

import boto3
import dash
import numpy as np
import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, ctx, dash_table
from dash.dependencies import ClientsideFunction, Input, Output, State
from dash.exceptions import PreventUpdate

from dynamofield.db import dynamodb_init, key_utils

from dynamofield.db import init_db, table_utils
from dynamofield.field import field_table, importer
from dynamofield.utils import json_utils
from app_import_panel import *
from app_query_panel import *

# def init_field_trial():

#     table_name = "ft_db"
#     # client = dynamodb_init.init_dynamodb_client()
#     # table_utils.delete_all_items(client, table_name)
#     dynamodb_server = dynamodb_init.DynamodbServer()
#     # client = dynamodb_server.init_dynamodb_client()
#     dynamodb_res = dynamodb_server.init_dynamodb_resources()
#     field_trial = field_table.FieldTable(dynamodb_res, table_name)
#     return field_trial


# field_trial = init_field_trial()
# item_counts = field_trial.get_item_count()

app = Dash(__name__, 
    # use_pages=True,
    suppress_callback_exceptions=True)



app.layout = html.Div(
    id="db",
    children=[
        # Banner
        html.Div(
            id="banner",
            className="banner",
            children=[html.H2("FT database.")],
        ),
        dcc.Tabs(id='tabs-function-1', value='tab-query', children=[
            dcc.Tab(label='Query database', value='tab-query'),
            dcc.Tab(label='Import data', value='tab-import'),
            dcc.Tab(label='Initialise database', value='tab-init-db'),
        ]),
        html.Div(id='tabs-function-content-1')

    ]
)


@app.callback(
    Output('tabs-function-content-1', 'children'),
    Input('tabs-function-1', 'value')
)
def render_panels(tab):
    if tab == "tab-query":
        return generate_query_panel()
    elif tab == "tab-import":
        return generate_import_panel()
    elif tab == "tab_init_db":
        return  html.Div([])


if __name__ == '__main__':
    app.run_server(debug=True)

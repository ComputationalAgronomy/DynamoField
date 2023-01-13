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
import dash_bootstrap_components as dbc
from dash.dependencies import ClientsideFunction, Input, Output, State
from dash.exceptions import PreventUpdate

from dynamofield.db import dynamodb_init, key_utils

from dynamofield.db import init_db, table_utils
from dynamofield.field import field_table, importer
from dynamofield.utils import json_utils
from app_panel_import import *
from app_panel_query import *
from app_panel_db_status import *
from callbacks import *

# theme = dbc.themes.ZEPHYR
external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]

app = Dash(__name__, 
    # use_pages=True,
    suppress_callback_exceptions=True,
    assets_folder='assetsX',
    external_stylesheets=external_stylesheets\
)


app.layout = html.Div(
    id="db",
    children=[
        # Banner
        html.Div(
            id="banner",
            className="banner",
            children=[html.H2("FT database.")],
        ),
        dcc.Store(id='store_server', storage_type='local'),
        dcc.Store(id='store_table', storage_type='local'),
        
        dcc.Store(id='store_db_info', storage_type='session', clear_data=False),
        dcc.Store(id='store_endpoint', storage_type='session', clear_data=False),
        dcc.Store(id='store_table_name', storage_type='session', clear_data=False),
        dcc.Store(id='store_db_status', storage_type='session', clear_data=False),
        dcc.Store(id='store_table_status', storage_type='session', clear_data=False),
        dcc.Tabs(id='tabs-function', value='tab-db-status', children=[
            dcc.Tab(label='Query database', value='tab-query'),
            dcc.Tab(label='Import data', value='tab-import'),
            dcc.Tab(label='Database Status', value='tab-db-status'),
        ]),
        html.Div(id='tabs-function-content')

    ]
)


@app.callback(
    Output('tabs-function-content', 'children'),
    Input('tabs-function', 'value')
)
def render_panels(tab):
    if tab == "tab-query":
        return generate_query_panel()
    elif tab == "tab-import":
        return generate_import_panel()
    elif tab == "tab-db-status":
        return generate_db_status_panel()


if __name__ == '__main__':
    app.run_server(debug=True)

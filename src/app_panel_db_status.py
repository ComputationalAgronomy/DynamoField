

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

from app_data import * #dynamodb_server  # field_trial
# from callbacks import *
import app_style


def update_status_panel():
    return html.Div(children=[
        dcc.Markdown(id="db_markdown",
                     dangerously_allow_html=True),
        # dcc.RadioItems(id="radio_db_status", 
        #                style={'display': 'flex', "margin-right": "5pt"},
        #                inline=False,
        #                options=[
        #     {'label': html.Div('DB Online', style={"color": "Green", "font-size": 16}), 'value': True}, #, 'disabled': True},
        #     {'label': html.Div(['DB Offline'], style={"color": "Red", "font-size": 16}), 'value': False},# , 'disabled': True},
        #     # {
        #     # "label": html.Div(['London'], style={'color': 'LightGreen', 'font-size': 20}),
        #     # "value": "London",
        # # },
          
        # ],),
    ],)

def update_config_panel():
    return html.Div(className="row",
                    style={
                        'margin': '10px'
                    },
                    children=[
        html.Div(className="three columns", children=[
            html.Label("Database endpoint:"),
            html.Label("Default: http://localhost:8000/"),
            dcc.Input(id="db_endpoint", type="text",
                      placeholder="http://localhost:8000/", debounce=True,
            ),
        ]),
        html.Div(className="three columns", children=[
            html.Label("Table name:"),
            html.Label("Default: ft_db"),
            dcc.Input(id="db_table_name", type="text",
                      placeholder="ft_db", debounce=True,
            ),
        ]),
        html.Button(className="three columns",
                    children='Connect Database', id='btn_connect_db',
                    n_clicks=0,  # style=app_style.btn_style,
                    style={"height":"200%"}
        ),
    ])


def generate_db_status_panel():
    return [
        html.Div(#style={'padding': 10, 'flex': 1},
                 children=[
            html.Br(),
            html.Div("aoeuaoeu"),
            dcc.RadioItems(['New York City', 'Montréal',
                            'San Francisco'], 'Montréal'),
            html.Div(id="get_item_count_db"),
            html.Br(),
            # dcc.Store(id='store_server', storage_type='local'),
            # dcc.Store(id='store_table', storage_type='local'),

        ]),
        dcc.Loading(
            id="loading-ep",
            type="default",
            children=html.Div(id="loading_update_db")
        ),
        html.Hr(),
        dcc.Interval(id="refresh-graph-interval", disabled=False, interval=10000),
        update_status_panel(),
        html.Hr(),
        update_config_panel(),
        html.Hr(),
        html.Button('Start database', id='btn_db_start',
                    n_clicks=0,  # style=app_style.btn_style,
                    className="two columns"
                    ),
        # ],),
        html.Hr(),
        html.Table([
            html.Thead([
                html.Tr(html.Th('Info stored in memory', colSpan="4")),
                # html.Tr([
                #     html.Th(html.Button('memory', id='memory-button')),
                #     html.Th(html.Button('localStorage', id='local-button')),
                #     html.Th(html.Button('sessionStorage', id='session-button'))
                # ]),
                html.Tr([
                    html.Th('Endpoint'),
                    html.Th('table_name'),
                    html.Th('DB status'),
                    html.Th('Table status')
                ])
            ]),
            html.Tbody([
                html.Tr([
                    html.Td(id='data_endpoint'),
                    html.Td(id='data_table_name'),
                    html.Td(id='data_db_status'),
                    html.Td(id='data_table_status'),
                ])
            ])
        ])
    ]


# @dash.callback(
#     Output("store_server", "data"),
#     Input("store_server", "data"),
# )
# def init_server(x):
#     dynamodb_server = init_dynamodb()
#     return dynamodb_server
#     #field_trial = init_field_trial(dynamodb_server)





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
    # Output('radio_db_status', 'value'),
    Output("db_markdown", "children"),
    # Output("loading-output-ep", "children"),
    Input("refresh-graph-interval", "n_intervals"),
    State('store_db_status', 'data'),
    State('store_table_status', 'data'),
)
def update_endpoint(btn, db_status, table_status):

    md_db = check_status(db_status)
    md_table = check_status(table_status)

    md_output = f"""<p style="margin: 0;font-size:20pt">
    Database status: {md_db}\t\t\tTable status: {md_table}
    </p>"""

    return md_output


# radio_db_status


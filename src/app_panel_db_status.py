

import base64
import datetime
import io
import os
from datetime import datetime as dt

import dash
import dash_bootstrap_components as dbc
import numpy as np
import pandas as pd
from dash import Dash, ctx, dash_table, dcc, html
from dash.dependencies import ClientsideFunction, Input, Output, State
from dash.exceptions import PreventUpdate

# from callbacks import *
import app_style
from app_data import *  # dynamodb_server  # field_trial
from dynamofield.db import dynamodb_init, init_db, key_utils, table_utils
from dynamofield.field import field_table, importer
from dynamofield.utils import json_utils


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
    return html.Div(style={'padding': 10},
                    children=[
        dbc.Row(children=[
            html.H4("Connect to existing database:"),
            dbc.Col([
                # html.Div(className="three columns", children=[
                html.Label("Database endpoint:"),
                html.Label("Default: http://localhost:8000/"),
                dcc.Input(id="db_endpoint", type="text",
                          placeholder="http://localhost:8000/", debounce=True,
                          ),
            ], width="auto"),
            dbc.Col([
                # html.Div(className="three columns", children=[
                html.Label("DB table name:"),
                html.Label("Default: ft_db"),
                dcc.Input(id="db_table_name", type="text",
                          placeholder="ft_db", debounce=True,
                          ),
            ], width="auto"),
            dbc.Col([
                dbc.Button(  # className="three columns",
                    children='Connect Database', id='btn_connect_db',
                    n_clicks=0, size="lg",  # style=app_style.btn_style,
                    style={
                        "margin": "20px", 'margin-top': '30px',
                        "height": "50px", "width": "200px",
                    }
                ),
            ], width="auto"),
            dbc.Col([
                dbc.Button(id="btn_list_tables", children="List existing tables",
                    n_clicks=0, size="lg",
                    style={
                        "margin": "20px", 'margin-top': '30px',
                        "height": "50px", "width": "200px",
                    }
                ),
            ], width="auto"),
        ])
    ])


def create_new_table_panel():
    return html.Div(style={'padding': 10},
                    children=[
        
        dbc.Row([
            dbc.Col([
                html.H4("Database table information"),
                dbc.Label("Create a new table. Table name:"),
                dbc.Input(id="new_table_name", type="text", minLength=3),
                dbc.Button(id="btn_create_table", children="Create new table",
                        n_clicks=0, size="lg", className="my-2"),
            ], width=3),
            dbc.Col([
                html.H4("Dangour zone!", style={"color": "red"}),    
                dbc.Label("DELETE a table. Table name:"),
                dbc.Input(id="text_delete_tablename", type="text", style={"width":"200px"}),
                dbc.Button(id="btn_delete_table", children="DELETE this table",
                    n_clicks=0, size="lg", color="danger",
                    className="my-2")
            ], width={"size": 3,  "offset": 3})
        ]),
        html.Br(),
        # dbc.Row([
        #     dbc.Col([
        #         dbc.Button(id="btn_list_tables", children="List existing tables",
        #                 n_clicks=0, size="lg",)
        #                 # style={"margin-top": "20px"})
        #     ], width={"size": 2, "offset": 0}),
        # ]),

        html.Br(),
        dcc.Markdown(id="db_table_md",
            dangerously_allow_html=True),
        dash_table.DataTable(id="dt_list_table",
            page_size=10,  # we have less data in this example, so setting to 20
            style_table={'height': '200px', 'overflowY': 'auto', 'width': '300px'}),
    ])



def delete_table_panel():
    return  html.Div(style={'padding': 10},
                    children=[
        
    ])




def db_debug_panel():
    return html.Table([
        html.Thead([
            html.Tr(html.Th('DEBUG: Info stored in memory', colSpan="4")),
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


def generate_db_status_panel():
    return [
        # html.Div(#style={'padding': 10, 'flex': 1},
        #          children=[
        #     # html.Br(),
        #     html.Div(id="get_item_count_db"),
        # ]),
        dcc.Loading(
            id="loading-ep",
            type="default",
            children=html.Div(id="loading_update_db")
        ),
        # html.Hr(),
        # update_status_panel(),
        html.Hr(),
        update_config_panel(),
        html.Hr(),
        dbc.Button('Start database (TODO)', id='btn_db_start',
                    n_clicks=0,  size="lg", # style=app_style.btn_style,
                    # className="two columns"
                    style={
                        # "padding":"5px",
                        "margin":"10px", #'margin-top': '0px', 
                        "height":"50px",  "width":"200px", 
                    }
        ),
        # ],),
        html.Hr(),
        create_new_table_panel(),
        delete_table_panel(),
        html.Hr(),
        db_debug_panel(),

        
    ]


# @dash.callback(
#     Output("store_server", "data"),
#     Input("store_server", "data"),
# )
# def init_server(x):
#     dynamodb_server = init_dynamodb()
#     return dynamodb_server
#     #field_trial = init_field_trial(dynamodb_server)





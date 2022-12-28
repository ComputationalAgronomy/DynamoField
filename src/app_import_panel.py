

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


item_counts = 10
def generate_import_panel():
    return [html.Div(children=[
            html.Br(),
            html.Div(f"Total item count: {item_counts}", id="get_item_count"),
            dcc.RadioItems(['New York City', 'Montréal',
                            'San Francisco'], 'Montréal'),
            html.Div(f"Total item count: {item_counts}", id="nths"),
            dcc.RadioItems(['New York City', 'Montréal',
                            'San Francisco'], 'Montréal'),

            dcc.Upload(
                id='upload-data',
                children=html.Div([
                    'Drag and Drop or ',
                    html.A('Select Files')
                ]),
                style={
                    'width': '100%',
                    'height': '60px',
                    'lineHeight': '60px',
                    'borderWidth': '1px',
                    'borderStyle': 'dashed',
                    'borderRadius': '5px',
                    'textAlign': 'center',
                    'margin': '10px'
                },
                # Allow multiple files to be uploaded
                multiple=True
            ),
            html.Div(id='output-data-upload'),
            ], style={'padding': 10, 'flex': 1}),


            # html.Div(children=[
            #     html.Label('Checkboxes'),
            #     dcc.Checklist(['New York City', 'Montréal', 'San Francisco'],
            #                   ['Montréal', 'San Francisco']
            #                   ),

            #     html.Br(),
            #     html.Label('Text Input'),
            #     dcc.Input(value='MTL', type='text'),

            # ], style={'padding': 10, 'flex': 1}
            # )
    ]


@dash.callback(
    Output('get_item_count', 'children'),
    Input('tabs-function-1', 'value')
)
def update_item_count(x):
    # if not value:
    #     raise PreventUpdate
    # # if value is not No?ne:
    # info = field_trial.list_all_sort_keys(value)
    # info_global = key_utils.extract_sort_key_prefix(info)
    # print(info_global[0])
    print(item_counts)
    return f"Total item count: {item_counts}-1"




def parse_contents(contents, filename, date):
    content_type, content_string = contents.split(',')

    decoded = base64.b64decode(content_string)
    try:
        if 'csv' in filename:
            # Assume that the user uploaded a CSV file
            df = pd.read_csv(
                io.StringIO(decoded.decode('utf-8')))
        elif 'xls' in filename:
            # Assume that the user uploaded an excel file
            df = pd.read_excel(io.BytesIO(decoded))
    except Exception as e:
        print(e)
        return html.Div([
            'There was an error processing this file.'
        ])

    return html.Div([
        html.H5(filename),
        html.H6(datetime.datetime.fromtimestamp(date)),

        dash_table.DataTable(
            df.to_dict('records'),
            [{'name': i, 'id': i} for i in df.columns]
        ),

        html.Hr(),  # horizontal line

        # For debugging, display the raw contents provided by the web browser
        html.Div('Raw Content'),
        html.Pre(contents[0:200] + '...', style={
            'whiteSpace': 'pre-wrap',
            'wordBreak': 'break-all'
        })
    ])

@dash.callback(Output('output-data-upload', 'children'),
              Input('upload-data', 'contents'),
              State('upload-data', 'filename'),
              State('upload-data', 'last_modified'))
def update_output(list_of_contents, list_of_names, list_of_dates):
    if list_of_contents is not None:
        children = [
            parse_contents(c, n, d) for c, n, d in
            zip(list_of_contents, list_of_names, list_of_dates)]
        return children





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

def generate_import_panel():
    return [
        html.Div(style={'padding': 10, 'flex': 1},
                 children=[
            html.Br(),
            html.Div(id="get_item_count"),            
            dcc.RadioItems(['New York City', 'Montréal',
                            'San Francisco'], 'Montréal'),
            # html.Div(f"Total item count: {item_counts}", id="nths"),
            dcc.RadioItems(['New York City', 'Montréal',
                            'San Francisco'], 'Montréal'),

            dcc.Upload(
                id='upload-data',
                children=html.Div([
                    'Drag and Drop or ',
                    html.A('Select Files')
                ]
                ),
                style={
                    'width': '80%',
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
            html.Div(className="row", children=[
                dcc.Markdown("Import data type:", className="two columns", id="import_markdown"),
                dcc.Input(id="importing_type", type="text", 
                    minLength=3, 
                    required=True, placeholder="", debounce=True,
                    className="three columns"),
                dcc.RadioItems(id="import_is_append",
                    options={"False": "Insert new data", "True": "Replace existing"},
                    value="False",
                    className="three columns"),
                html.Button('Import data', id='import_data',
                    n_clicks=0, #style=app_style.btn_style,
                    className="four columns"),
            ]),

            html.Div(id='output-data-upload'),
        ],),


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



def parse_contents(contents, filename, date, data_type, is_append):

    content_type, content_string = contents.split(',')
    print(3)
    decoded = base64.b64decode(content_string)
    try:
        if 'csv' in filename:
            # Assume that the user uploaded a CSV file
            df = pd.read_csv(
                io.StringIO(decoded.decode('utf-8')))
            # data_importer = importer.DataImporter(filename, data_type)
        elif 'xls' in filename:
            # Assume that the user uploaded an excel file
            df = pd.read_excel(io.BytesIO(decoded))
        print(df)
        data_importer = importer.DataImporter(df, data_type)
        print(2222, is_append, type(is_append))
        data_importer.parse_df_to_dynamo_json(append=is_append, field_trial=field_trial)
        print(3333)
        import_len = field_trial.import_batch_field_data_res(data_importer) # How to test this effectively?
    except Exception as e:
        print(e)
        return html.Div([
            f'There was an error processing this file.\n{e}'
        ])

    return html.Div([
        html.H5(filename),
        html.H6(datetime.datetime.fromtimestamp(date)),
        html.H6(f"Imported {import_len} rows and store in info={data_type}."),
        dash_table.DataTable(df.to_dict('records'),
            [{'name': i, 'id': i} for i in df.columns]
        ),

        html.Hr(),  # horizontal line

        # For debugging, display the raw contents provided by the web browser
        html.Div('Raw Content'),
        html.Pre(contents[0:10] + '...', style={
            'whiteSpace': 'pre-wrap',
            'wordBreak': 'break-all'
        })
    ])


@dash.callback(Output("upload-data", "children"),
               Output("import_markdown", "children"),
               Input("upload-data", "filename"),
               Input("importing_type", "value"),
              )
def update_uploader_info(filename, data_type):
    parsed_name = ""
    parsed_data_type = "Import data type:"
    if filename is not None:
        parsed_name = f"\nCurrent files: {filename}"
    if data_type is not None:
        parsed_data_type = f"{parsed_data_type} {data_type}"
    return [
        html.Div([
            'Drag and Drop or ',
            html.A('Select Files    '),
            parsed_name
        ]),
        f"{parsed_data_type}  {parsed_name} "
    ]

@dash.callback(Output('output-data-upload', 'children'),
               Input('import_data', 'n_clicks'),
               State('upload-data', 'contents'),
               State('upload-data', 'filename'),
               State('upload-data', 'last_modified'),
               State('importing_type', 'value'),
               State("import_is_append", "value")
              )
def update_output(n_clicks, list_of_contents, list_of_names, list_of_dates,
                  data_type, is_append):
    is_append = eval(is_append)
    print(f"{data_type}, {is_append}, {list_of_names}")
    if list_of_contents is not None:
        children = [parse_contents(c, n, d, data_type, is_append)
                    for c, n, d in
                    zip(list_of_contents, list_of_names, list_of_dates)]
        return children



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
from app_data import *
from dynamofield.db import dynamodb_init, init_db, key_utils, table_utils
from dynamofield.field import field_table, importer
from dynamofield.utils import json_utils

# item_counts = field_trial.get_item_count()

def generate_import_panel():
    BTN_STYLE = {
        "margin": "10px", 'margin-top': '10px',
        "width": "200px", "height": "60px",
        'align-items': 'center', 'justify-content': 'center'
    }
    return [
        html.Div(style={'padding': 10, 'flex': 1},
                #  className="row",
                 children=[
            # html.Br(),
            # html.Div(id="get_item_count"),            
            # dcc.RadioItems(['New York City', 'Montréal',
            #                 'San Francisco'], 'Montréal'),
            html.Hr(),
            # # html.Div(f"Total item count: {item_counts}", id="nths"),
            # dcc.RadioItems(['New York City', 'Montréal',
            #                 'San Francisco'], 'Montréal'),
            dbc.Row([
                dbc.Col([
            # html.Div(className="row", children=[
                    dcc.Upload(
                        id='upload-data',
                        # className="five columns",
                        children=html.Div([
                            'Drag and Drop or ',
                            html.A('Select Files')
                        ]
                        ),
                        style={
                            'width': '100%',
                            'height': '60px',
                            'lineHeight': '60px',
                            'borderWidth': '1px',
                            'borderStyle': 'dashed',
                            'borderRadius': '5px',
                            'textAlign': 'center',
                            'margin': '5px'
                        },
                        # Allow multiple files to be uploaded
                        multiple=True
                    )
                ], width=4),
                dbc.Col([
                    dbc.Button('Preview file', id='btn_preview',
                            n_clicks=0, size="lg",
                            # className="me-2",
                            style=BTN_STYLE, 
                    )
                ], width="auto"),
            ]),
            dbc.Row([
                dbc.Col([
            # html.Div(className="row", 
            #          style={
            #             'margin': '10px'
            #          },
            #          children=[
            #     html.Div(className="three columns", children=[
                    html.H5("Import data type"),
                    # html.Br(),
                    dbc.Input(id="importing_type",
                        type="text", 
                        required="required",
                        minlength=3, #maxLength=-1,
                        # type="number",
                        
                    ),
                ], width=3),
                dbc.Col([
                    dcc.RadioItems(id="import_is_append",
                        options={"False": "Insert new data", "True": "Replace existing"},
                        value="False",
                        style={
                            "margin":"30px", 'margin-top': '20px', 
                        }
                        ),
                ], width=3),
                dbc.Col([
                    dbc.Button('Import data', id='btn_import',
                        n_clicks=0, size="lg",
                        className="me-2",
                        style=BTN_STYLE, 
                    ),
                # ]),
                ], width=3),
            ]),
            html.Hr(),
            html.Div(className="row", children=[
                dcc.Markdown("Import data type:", className="two columns", id="import_markdown"),

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
    markdown_text = f"{parsed_data_type}  {parsed_name}"
    return [
        html.Div([
            'Drag and Drop or ',
            html.A('Select Files    '),
            parsed_name
        ]),
        markdown_text
    ]

    

@dash.callback(Output("btn_import", "disabled"),
               Input("importing_type", "value"),
               Input('upload-data', 'filename'),
               Input("importing_type", "required"),
               Input("importing_type", "style"),
              )
def update_uploader_info(data_type, filenames, r, s):
    is_disabled = True
    if data_type is not None and filenames is not None:
        is_disabled = False
    # else if 
    #     print(f"data_type:{data_type}={data_type is not None}={len(data_type)>1}={is_disabled}")
    print(r, s)
    print(f"validate import button: {data_type}___{filenames}")
    print(f"data_type:{data_type}={data_type is not None}=={is_disabled}")
    return is_disabled    




def parse_contents(contents, filename, date=None):

    content_type, content_string = contents.split(',')
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
        else:
            raise Exception("Invalid file type.")
    except Exception as e:
        print(e)
        df = pd.DataFrame({
            'There was an error processing this file': 
                f"Error message: {str(e)}"
            }, index=[0])
        # return html.Div([
        #     f'There was an error processing this file.\n{e}'
        # ])

    return df


    
def preview_content(contents, filename, date):
    df = parse_contents(contents, filename, date)
    return html.Div([
        html.H5(filename),
        html.H6(datetime.datetime.fromtimestamp(date)),
        dash_table.DataTable(df.to_dict('records'),
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


def import_dataframe(contents, filename, data_type, is_append, field_trial):
    #     content_type, content_string = contents.split(',')
    # decoded = base64.b64decode(content_string)
    
    try:
        df = parse_contents(contents, filename)
        data_importer = importer.DataImporter(df, data_type)
        data_importer.parse_df_to_dynamo_json(append=is_append, field_trial=field_trial)
        import_len = field_trial.import_batch_field_data_res(data_importer) # How to test this effectively?
    except Exception as e:
        print(e)
        return html.Div([
            f'There was an error processing this file.<br>{e}'
        ])

    return html.Div([
        html.H5(filename),
        # html.H6(datetime.datetime.fromtimestamp(date)),
        dcc.Markdown(f"Imported **{import_len}** rows and store in info={data_type}."),
        # dash_table.DataTable(df.to_dict('records'),
        #     [{'name': i, 'id': i} for i in df.columns]
        # ),
    ])


@dash.callback(Output('output-data-upload', 'children'),
               Input('btn_import', 'n_clicks'),
               Input('btn_preview', 'n_clicks'),
               State('upload-data', 'contents'),
               State('upload-data', 'filename'),
               State('upload-data', 'last_modified'),
               State('importing_type', 'value'),
               State("import_is_append", "value"),
               State('store_db_info', 'data'),
               )
def update_output(btn_1, btn_2,
                  list_of_contents, list_of_names, list_of_dates,
                  data_type, is_append, db_info):
    children = []
    is_append = eval(is_append)
    print(f"{data_type}, {is_append}, {list_of_names}")
    if list_of_contents is not None:
        if "btn_preview" == ctx.triggered_id:
            children = [preview_content(c, n, d) for c, n, d in
                        zip(list_of_contents, list_of_names, list_of_dates)]
        elif "btn_import" == ctx.triggered_id:
            # if not db_info["db_status"] or not db_info["table_status"]:
            #     children = ([html.H5("Database not available")])
            print(f"data_type_{data_type}")
            field_trial = connect_db_table(db_info)
            children = [import_dataframe(c, n, data_type, is_append, field_trial)
                        for c, n, in
                        zip(list_of_contents, list_of_names)]
            # else:
                # children = html.Div([html.H5("Please enter data type")])
    return children


data_very_complex = {
    "key_str": "value_str",
    "key_int": 5106,
    "Key_float": 3.1415,
    "key_bool": False,
    "key_list": [1, "a"],          #  list as value
    "key_dict": {"k1": "v1", "k2": "v2"}    #  dict as value
}

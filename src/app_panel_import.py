

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
import app_data
from dynamofield.db import dynamodb_init, init_db, key_utils, table_utils
from dynamofield.field import field_table, importer
from dynamofield.utils import json_utils


BTN_STYLE = {
    'margin': '10px', 'margin-top': '10px',
    'height': '60px', 'width': '200px',
    'align-items': 'center', 'justify-content': 'center',
    'text-transform': 'none',
}

UPLOAD_STYLE = {
    'width': '100%',
    'height': '100px',
    'lineHeight': '60px',
    'borderWidth': '1px',
    'borderStyle': 'dashed',
    'borderRadius': '5px',
    'textAlign': 'center',
    'margin': '5px'
}


def upload_import_panel():
    return html.Div(style={'padding': 10},
                    children=[
        dbc.Row([
            dbc.Col([
                dcc.Upload(
                    id='upload-data',
                    children=html.Div([
                        'Drag and Drop or ',
                        html.A('Select Files')
                    ]),
                    style=UPLOAD_STYLE,
                    multiple=True
                )
            ], width=5),
            dbc.Col([
                dbc.Button(id='btn_preview', children='Preview file',
                           **app_style.BTN_ACTION_CONF,
                           ),
            ], width="auto"),
        ]),
        dbc.Row([
            dbc.Col([
                html.H5("Import data type (REQUIRED)"),
                dbc.Input(id="importing_type",
                          type="text", required=True,
                          minlength=3,  # maxLength=-1,
                          ),
            ], width=5),
            dbc.Col([
                dcc.RadioItems(id="import_is_append", value="False",
                               options={
                                   "False": "Insert new data",
                                   "True": "Replace existing"},
                               style={
                                   "margin": "30px", 'margin-top': '20px',
                               }
                               ),
            ], width=3),
            dbc.Col([
                dbc.Button(id='btn_import', children='Import data',
                           **app_style.BTN_ACTION_CONF,
                           ),
            ], width="auto"),
        ])
    ])




def danger_delete_data_type_panel():
    return html.Div(style={'padding': 10},
                    children=[
        dbc.Card([
            dbc.CardHeader(
                html.H4("Danger Zone!",style={"color": "red"})),
            dbc.CardBody([
                dbc.Label("DELETE a data type"),
                dbc.Input(id="text_delete_data_type",
                          type="text"),
                dbc.Button(id="btn_delete_data_type", children="DELETE this data type",
                           color="danger",
                           **app_style.BTN_ACTION_CONF,)
            ]),
            dcc.Markdown(id="md_delete_output")
        ]),

    ])

def generate_import_panel():


    return [html.Div(style={'padding': 10, 'flex': 1}, id="generate_import",
                     children=[
        upload_import_panel(),
        html.Hr(style={"height": "2px", "margin": "5px"}),
        html.Div(className="row", children=[
            dcc.Markdown("Import data type:", className="two columns", id="import_markdown"),
        ]),
        html.Div(id='output-data-upload'),
        html.Hr(style={"height": "2px", "margin": "5px"}),
        danger_delete_data_type_panel()
    ])
    ]


@dash.callback(
    Output("upload-data", "children"),
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
            'Drag and Drop or ', html.A('Select Files    '),
            parsed_name
        ]),
        markdown_text
    ]


@dash.callback(
    Output("btn_import", "disabled"),
    Input("importing_type", "value"),
    Input('upload-data', 'filename'),
    Input("importing_type", "required"),
    Input("importing_type", "style"),
)
def is_btn_import_disabled(data_type, filenames, r, s):
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
    col_name_dict = [{'name': i, 'id': i} for i in df.columns]
    return html.Div([
        html.H5(filename),
        html.H6(datetime.datetime.fromtimestamp(date)),
        dash_table.DataTable(df.to_dict('records'), col_name_dict),
        html.Hr(style={"height": "2px", "margin": "5px"}),
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
        data_importer.parse_df_to_dynamo_json(
            append=is_append, field_trial=field_trial)
        import_len = field_trial.import_batch_field_data_res(
            data_importer)  # How to test this effectively?
    except Exception as e:
        print(e)
        return html.Div([
            f'There was an error processing this file.<br>{e}'
        ])

    return html.Div([
        html.H5(filename),
        # html.H6(datetime.datetime.fromtimestamp(date)),
        dcc.Markdown(
            f"Imported **{import_len}** rows and store in info={data_type}."),
        # dash_table.DataTable(df.to_dict('records'),
        #     [{'name': i, 'id': i} for i in df.columns]
        # ),
    ])


@dash.callback(
    Output('output-data-upload', 'children'),
    Input('btn_import', 'n_clicks'),
    Input('btn_preview', 'n_clicks'),
    State('upload-data', 'contents'),
    State('upload-data', 'filename'),
    State('upload-data', 'last_modified'),
    State('importing_type', 'value'),
    State("import_is_append", "value"),
    State('store_db_info', 'data'),
    prevent_initial_call=True,
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
            field_trial = app_data.connect_db_table(db_info)
            children = [import_dataframe(c, n, data_type, is_append, field_trial)
                        for c, n, in
                        zip(list_of_contents, list_of_names)]
            # else:
            # children = html.Div([html.H5("Please enter data type")])
    return children






@dash.callback(
    Output('md_delete_output', 'children'),
    Input('btn_delete_data_type', 'n_clicks'),
    State('text_delete_data_type', 'value'),
    State('store_db_info', 'data'),
    prevent_initial_call=True,
)
def delete_data_type(btn_delete, data_type, db_info):
    if data_type is None:
        raise PreventUpdate
    try:
        md = app_data.delete_all_data_type(db_info, data_type)
    except Exception as e:
        md = f"Please enter a data_type to delete all items. {e}"
    return md

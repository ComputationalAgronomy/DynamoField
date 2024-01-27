
import dash
import dash_bootstrap_components as dbc
from dash import dash_table, dcc, html
from dynamofield import app_db, app_style

BTN_STYLE = {
    'margin': '10px', 'margin-top': '10px',
    'height': '60px', 'width': '200px',
    'align-items': 'center', 'justify-content': 'center',
    'text-transform': 'none',
}

UPLOAD_STYLE = {
    'width': '100%',
    'height': '100px',
    # 'lineHeight': '20px',
    'borderWidth': '1px',
    'borderStyle': 'dashed',
    'borderRadius': '5px',
    'textAlign': 'center',
    # 'margin': '20px'
}

def upload_import_panel():
    return html.Div(style={'padding': 10},
                    children=[
        dbc.Row([
            dbc.Col([
                dcc.Upload(
                    id='upload-data',
                    # children=html.Div([
                    #     'Drag and Drop or ',
                    #     html.A('Select Files')
                    # ]),
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
                dbc.RadioItems(id="import_is_append", value="True",
                               options={
                                   "True": "Insert and append new data.",
                                #    "False": "Replace all existing records."
                               },
                               style={
                                   "margin": "20px",  # 'padding-top': '30px',
                               }
                               ),
            ], width="auto"),
            dbc.Col([
                dbc.Button(id='btn_import', children='Import data',
                           **app_style.BTN_ACTION_CONF,
                           ),
            ], width="auto"),
        ]),
        html.Hr(style={"height": "2px", "margin": "5px"}),
        html.Div(children=[
            dcc.Markdown(id="import_markdown"),
        ]),
        html.Div(id='output-data-upload'),
        html.Hr(style={"height": "2px", "margin": "5px"}),
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
                dbc.Button(id="btn_delete_data_type", children=["DELETE this data type"],
                           color="danger",
                           **app_style.BTN_ACTION_CONF,)
            ]),
            dcc.Markdown(id="md_delete_output")
        ], outline=True, color="danger"),

    ])


def generate_import_panel():
    return [html.Div(style={'padding': 10},
                     id="generate_import",
                     children=[
        upload_import_panel(),
        danger_delete_data_type_panel()
    ])]

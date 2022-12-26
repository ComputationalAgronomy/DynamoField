# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.


import datetime
# import field
import importlib
import os
from datetime import datetime as dt

import boto3
import dash
# import dash_core_components as dcc
# import dash_html_components as html
import numpy as np
import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, ctx, dash_table
from dash.dependencies import ClientsideFunction, Input, Output, State
from dash.exceptions import PreventUpdate

from dynamofield.db import dynamodb_init

from dynamofield.db import init_db, table_utils
from dynamofield.field import field_table, importer
from dynamofield.utils import json_utils


def init_field_trial():

    table_name = "ft_db"
    # client = dynamodb_init.init_dynamodb_client()
    # table_utils.delete_all_items(client, table_name)
    dynamodb_server = dynamodb_init.DynamodbServer()
    # client = dynamodb_server.init_dynamodb_client()
    dynamodb_res = dynamodb_server.init_dynamodb_resources()
    field_trial = field_table.FieldTable(dynamodb_res, table_name)
    return field_trial


field_trial = init_field_trial()

app = Dash(__name__)


df = pd.read_csv('gdp-life-exp-2007.csv')
# df = pd.read_csv('https://git.io/Juf1t')


fig = px.scatter(df, x="gdp per capita", y="life expectancy",
                 size="population", color="continent", hover_name="country",
                 log_x=True, size_max=60)

# app.layout = html.Div([
#     dcc.Graph(
#         id='life-exp-vs-gdp',
#         figure=fig
#     )
# ])


def build_upper_left_panel():
    return html.Div(
        id="upper-left",
        className="six columns",
        children=[
            html.P(
                className="section-title",
                children="Choose hospital on the map or procedures from the list below to see costs",
            ),
            html.Div(
                className="control-row-1",
                children=[
                    html.Div(
                        id="state-select-outer",
                        children=[
                            html.Label("Select a State"),
                            dcc.Dropdown(
                                id="state-select",
                                # options=[{"label": i, "value": i} for i in state_list],
                                # value=state_list[1],
                            ),
                        ],
                    ),
                    html.Div(
                        id="select-metric-outer",
                        children=[
                            html.Label("Choose a Cost Metric"),
                            dcc.Dropdown(
                                id="metric-select",
                                # options=[{"label": i, "value": i} for i in cost_metric],
                                # value=cost_metric[0],
                            ),
                        ],
                    ),
                ],
            ),
            html.Div(
                id="region-select-outer",
                className="control-row-2",
                children=[
                    html.Label("Pick a Region"),
                    html.Div(
                        id="checklist-container",
                        children=dcc.Checklist(
                            id="region-select-all",
                            options=[
                                {"label": "Select All Regions", "value": "All"}],
                            value=[],
                        ),
                    ),
                    html.Div(
                        id="region-select-dropdown-outer",
                        children=dcc.Dropdown(
                            id="region-select", multi=True, searchable=True,
                        ),
                    ),
                ],
            ),
            html.Div(
                id="table-container",
                className="table-container",
                children=[
                    html.Div(
                        id="table-upper",
                        children=[
                            html.P("Hospital Charges Summary"),
                            dcc.Loading(
                                children=html.Div(
                                    id="cost-stats-container")),
                        ],
                    ),
                    html.Div(
                        id="table-lower",
                        children=[
                            html.P("Procedure Charges Summary"),
                            dcc.Loading(
                                children=html.Div(
                                    id="procedure-stats-container")
                            ),
                        ],
                    ),
                ],
            ),
        ],
    )


# app.layout = html.Div(
#     # className="container scalable",
#     id="app-container",
#     children=[
#         html.Div(
#             id="banner",
#             className="banner",
#             children=[
#                 html.H6("Dash Clinical Analytics"),
#                 # html.Img(src=app.get_asset_url("plotly_logo_white.png")),
#             ],
#         ),
#         html.Div(
#             id="left-column",
#             # className="row",
#             className="four columns",
#             children=[
#                 build_upper_left_panel()
#             ]
#         ),
#       html.Div(
#             id="right-column",
#             className="eight columns",
#             children=[
#                 dcc.Graph(
#                     id="procedure-plot",
#                     # figure=generate_procedure_plot(
#                     #     data_dict[state_list[1]], cost_metric[0], init_region, []
#                     # ),
#                 )
#             ],
#         ),

#     ])

# app.layout = html.Div([
#     html.Div(children=[
#         html.Label('Dropdown'),
# dcc.Dropdown(['New York City', 'Montréal', 'San Francisco'],
# 'Montréal'),

#         html.Br(),
#         html.Label('Multi-Select Dropdown'),
#         dcc.Dropdown(['New York City', 'Montréal', 'San Francisco'],
#                      ['Montréal', 'San Francisco'],
#                      multi=True),

#         html.Br(),
#         html.Label('Radio Items'),
#         dcc.RadioItems(['New York City', 'Montréal', 'San Francisco'], 'Montréal'),
#     ], style={'padding': 10, 'flex': 1}),

#     html.Div(children=[
#         html.Label('Checkboxes'),
#         dcc.Checklist(['New York City', 'Montréal', 'San Francisco'],
#                       ['Montréal', 'San Francisco']
#         ),

#         html.Br(),
#         html.Label('Text Input'),
#         dcc.Input(value='MTL', type='text'),

#         html.Br(),
#         html.Label('Slider'),
#         dcc.Slider(
#             min=0,
#             max=9,
#             marks={i: f'Label {i}' if i == 1 else str(i) for i in range(1, 6)},
#             value=5,
#         ),
#     ], style={'padding': 10, 'flex': 1}),
#     dcc.Graph(
#         id='life-exp-vs-gdp',
#         figure=fig
#     )
# ], style={'display': 'flex', 'flex-direction': 'row'})


def description_panel():
    return html.Div(
        id="description-panel",
        children=[
            # html.H5("Field trial analysis"),
            html.H3("Welcome to the interactive Dashboard"),
            html.Div(
                id="intro",
                children="Explore clinic patient volume by time of day, waiting time, and care score. Click on the heatmap to visualize patient experience at different time points.",
            ),
        ],
    )


trial_list = [1, 3, 4]


def generate_control_panel():
    """
    :return: A Div containing controls for graphs.
    """
    return html.Div(
        id="control-card",
        children=[
            html.P("Select Clinic"),
            dcc.Dropdown(
                id="clinic-select",
                # options=[{"label": i, "value": i} for i in trial_list],
                # value=clinic_list[0],
            ),
            html.Br(),
            # html.P("Select info"),
            # dcc.DatePickerRange(
            #     id="date-picker-select",
            #     start_date=dt(2014, 1, 1),
            #     end_date=dt(2014, 1, 15),
            #     min_date_allowed=dt(2014, 1, 1),
            #     max_date_allowed=dt(2014, 12, 31),
            #     initial_visible_month=dt(2014, 1, 1),
            # ),
            html.Br(),
            # html.Br(),
            html.P("Select Info"),
            dcc.Dropdown(
                id="admit-select",
                # options=[{"label": i, "value": i} for i in admit_list],
                # value=admit_list[:],
                multi=True,
            ),
            html.Br(),
            html.Div(
                id="reset-btn-outer",
                children=html.Button(
                    id="reset-btn", children="Reset", n_clicks=0),
            ),
        ],
    )


app.layout = html.Div(
    id="app-container",
    children=[
        # Banner
        html.Div(
            id="banner",
            className="banner",
            children=[html.H4("Field trial database.")],
        ),
        # Left column
        html.Div(className='row',
                 children=[
                     html.Div(
                         id="left-column",
                         className="six columns",
                         children=[
                             description_panel(),
                             generate_control_panel()]
                         # + [
                         #     html.Div(
                         #         ["initial child"], id="output-clientside", style={"display": "none"}
                         #     )
                         # ],
                     ),
                     # Right column
                     html.Div(
                         id="right-column",
                         className="six columns",
                         children=[
                             # Patient Volume Heatmap
                             html.Div(
                                 id="patient_volume_card",
                                 children=[
                                     html.B("Patient Volume"),
                                     html.Hr(),
                                     # dcc.Graph(id="patient_volume_hm"),
                                 ],
                             ),
                             # Patient Wait time by Department
                             html.Div(
                                 id="wait_time_card",
                                 children=[
                                     html.B(
                                         "Patient Wait Time and Satisfactory Scores"),
                                     html.Hr(),
                                     # html.Div(id="wait_time_table",
                                     # children=initialize_table()),
                                 ],
                             ),
                         ],
                     ),
                 ]),
    ]
)

ids = field_trial.get_all_trial_id()

app.layout = html.Div(
    id="app-container",
    children=[
        # Banner
        html.Div(
            id="banner",
            className="banner",
            children=[html.H4("Field trial database.")],
        ),
        html.Div([
            html.Div(
                children=[
                    html.Label('Select trial ID'),
                    html.Br(),
                    dcc.Dropdown(options=ids, multi=False, id="select_trial"),
                ],
                style={'padding': 10, 'flex': 1}
            ),
            html.Div(
                children=[
                    html.Label(
                        'Multi-Select Information related to this trial'),
                    html.Br(),
                    dcc.Dropdown(id="update_info_list", multi=True),
                    html.Button('Select All', id='button_info_all', n_clicks=0),
                    html.Button('Select None', id='button_info_none', n_clicks=0),
                ],
                style={'padding': 10, 'flex': 1}
            ),
        ],
            style={'display': 'flex', 'flex-direction': 'row'}
        ),

        html.Div(children=[
            html.Br(),
            html.Label('Radio Items'),
            dcc.RadioItems(['New York City', 'Montréal',
                            'San Francisco'], 'Montréal'),
        ], style={'padding': 10, 'flex': 1}),

        html.Div(children=[
            html.Label('Checkboxes'),
            dcc.Checklist(['New York City', 'Montréal', 'San Francisco'],
                          ['Montréal', 'San Francisco']
                          ),

            html.Br(),
            html.Label('Text Input'),
            dcc.Input(value='MTL', type='text'),
            html.Button('Fetch data', id='fetch_data', n_clicks=0),
        ], style={'padding': 10, 'flex': 1}
        ),
        dash_table.DataTable(id="data_table",
            # data=df.to_dict('records'),
            # columns=[{"name": i, "id": i} for i in df.columns]
        )
    ]
)  # ,  # style={'display': 'flex', 'flex-direction': 'row'})

# ]
# )

info_global = []  # FIXME: HACK:
@ app.callback(
    Output('update_info_list', 'options'),
    Input('select_trial', 'value')
)
def update_output_info(value):
    if not value:
        raise PreventUpdate
    # if value is not No?ne:
    info = field_trial.list_all_sort_keys(value)
    info_global = field_table.FieldTable.extract_sort_key_prefix(info)
    print(info_global[0])
    return info_global
    # return f"aoeuaoeu {value}"


@app.callback(
    Output('update_info_list', 'value'),
    Input('button_info_all', 'n_clicks'),
    Input('button_info_none', 'n_clicks'),
    State('update_info_list', 'options'),
)
def update_output(b1, b2, options):
    if "button_info_all" == ctx.triggered_id:
        return options
    elif "button_info_none" == ctx.triggered_id:
        return None




@app.callback(
    [Output("data_table", "columns"), Output("data_table", "data")],
    [Input("fetch_data", "n_clicks")],
    State('select_trial', 'value'),
    State('update_info_list', 'value'),
)
def update_data_table(click, trial_id, info_list):
    if not trial_id:
        raise PreventUpdate
    print(trial_id)
    print(info_list)
    data = field_trial.get_multi_trial_id(trial_id)#, info_list[0])
    df = json_utils.result_list_to_df(data)
    print(df)
    columns = [{"name": i, "id": i} for i in df.columns]
    return columns, df.to_dict('records')


# @app.callback(
#     Output('dd-output-container', 'children'),
#     Input('demo-dropdown', 'value')
# )
# def update_output(value):
#     return f'You have selected {value}'

if __name__ == '__main__':
    app.run_server(debug=True)

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
# import dash_core_components as dcc
# import dash_html_components as html
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

app = Dash(__name__, 
    # use_pages=True,
    suppress_callback_exceptions=True)


# df = pd.read_csv('gdp-life-exp-2007.csv')
# df = pd.read_csv('https://git.io/Juf1t')


# fig = px.scatter(df, x="gdp per capita", y="life expectancy",
#                  size="population", color="continent", hover_name="country",
#                  log_x=True, size_max=60)


# def description_panel():
#     return html.Div(
#         id="description-panel",
#         children=[
#             # html.H5("Field trial analysis"),
#             html.H3("Welcome to the interactive Dashboard"),
#             html.Div(
#                 id="intro",
#                 children="Explore clinic patient volume by time of day, waiting time, and care score. Click on the heatmap to visualize patient experience at different time points.",
#             ),
#         ],
#     )



# def generate_control_panel():
#     """
#     :return: A Div containing controls for graphs.
#     """
#     return html.Div(
#         id="control-card",
#         children=[
#             html.P("Select Clinic"),
#             dcc.Dropdown(
#                 id="clinic-select",
#                 # options=[{"label": i, "value": i} for i in trial_list],
#                 # value=clinic_list[0],
#             ),
#             html.Br(),
#             # html.P("Select info"),
#             # dcc.DatePickerRange(
#             #     id="date-picker-select",
#             #     start_date=dt(2014, 1, 1),
#             #     end_date=dt(2014, 1, 15),
#             #     min_date_allowed=dt(2014, 1, 1),
#             #     max_date_allowed=dt(2014, 12, 31),
#             #     initial_visible_month=dt(2014, 1, 1),
#             # ),
#             html.Br(),
#             # html.Br(),
#             html.P("Select Info"),
#             dcc.Dropdown(
#                 id="admit-select",
#                 # options=[{"label": i, "value": i} for i in admit_list],
#                 # value=admit_list[:],
#                 multi=True,
#             ),
#             html.Br(),
#             html.Div(
#                 id="reset-btn-outer",
#                 children=html.Button(
#                     id="reset-btn", children="Reset", n_clicks=0),
#             ),
#         ],
#     )


# app.layout = html.Div(
#     id="app-ft-db",
#     children=[
#         # Banner
#         html.Div(
#             id="banner",
#             className="banner",
#             children=[html.H4("Field trial database.")],
#         ),
#         # Left column
#         html.Div(className='row',
#                  children=[
#                      html.Div(
#                          id="left-column",
#                          className="six columns",
#                          children=[
#                              description_panel(),
#                              generate_control_panel()]
#                          # + [
#                          #     html.Div(
#                          #         ["initial child"], id="output-clientside", style={"display": "none"}
#                          #     )
#                          # ],
#                      ),
#                      # Right column
#                      html.Div(
#                          id="right-column",
#                          className="six columns",
#                          children=[
#                              # Patient Volume Heatmap
#                              html.Div(
#                                  id="patient_volume_card",
#                                  children=[
#                                      html.B("Patient Volume"),
#                                      html.Hr(),
#                                      # dcc.Graph(id="patient_volume_hm"),
#                                  ],
#                              ),
#                              # Patient Wait time by Department
#                              html.Div(
#                                  id="wait_time_card",
#                                  children=[
#                                      html.B(
#                                          "Patient Wait Time and Satisfactory Scores"),
#                                      html.Hr(),
#                                      # html.Div(id="wait_time_table",
#                                      # children=initialize_table()),
#                                  ],
#                              ),
#                          ],
#                      ),
#                  ]),
#     ]
# )

item_counts = field_trial.get_item_count()


btn_style = {"margin-right": "10px", "margin-left": "10px", "margin-top": 3}
def generate_query_panel():
    return [
        html.Div(id="query_panel", children=[
            html.Div(children=[
                html.Label('Select trial ID'),
                html.Br(),
                dcc.Dropdown(options=ids, multi=False, id="select_trial"),
                html.Button('Fetch data', id='fetch_data', n_clicks=0, style=btn_style),
            ],
                style={'padding': 10, 'flex': 1}
            ),
            html.Div(children=[
                html.Label('Multi-Select Information related to this trial'),
                html.Br(),
                dcc.Dropdown(id="dropdown_info_sortkey", multi=True),
                html.Button('Select All', id='button_info_all', n_clicks=0, style=btn_style),
                html.Button('Select None', id='button_info_none', n_clicks=0, style=btn_style),
            ],
                style={'padding': 10, 'flex': 1}
            ),
        ],
            style={'display': 'flex', 'flex-direction': 'row'}
        ),
        
        
        html.Hr(),
        # html.Button('Fetch plot info', id='fetch_plot', n_clicks=0, style=btn_style),
        # html.H1("Figure"),
        html.Div(children=[
            html.Div(children=[
                dcc.Markdown("**X-axis**\n"),
                # html.Div("<b>aoeuaoeu</b>"),
                dcc.Dropdown(id="dropdown_xaxis", multi=False),
                html.Br(),
                html.Label('Plot types:'),
                dcc.RadioItems(["Scatter", "Line", "Bar"], "Scatter", id="raido-plot-type"),
            ], style={'padding': 10, 'flex': 1}),
            html.Div(children=[
                dcc.Markdown("**Y-axis**\n"),
                dcc.Dropdown(id="dropdown_yaxis", multi=False),
                html.Button("Plot data", id="btn_plot", style=btn_style),
            ], style={'padding': 10, 'flex': 1}),
        ], style={'display': 'flex', 'padding': 10, 'flex-direction': 'row'}),
        html.Hr(),
        html.H5("Table"),
        html.Br(),html.Br(),
        html.Button("Export data table (CSV)", id="btn_export", style=btn_style),
        dcc.Download(id="export_data"),
        
        # html.Div(
        #     "To download the figure, hover over the graph and click the camera icon.",
        #     style={"textAlign": "right"},
        # ),
        html.Br(),
        dash_table.DataTable(id="data_table", 
            page_size=30,  # we have less data in this example, so setting to 20
            style_table={'height': '300px', 'overflowY': 'auto'},
            export_format='csv'),
        dcc.Graph(id='data_figure'),
    
    ]



ids = field_trial.get_all_trial_id()
    
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


@ app.callback(
    Output('dropdown_info_sortkey', 'options'),
    Input('select_trial', 'value')
)
def update_output_info(value):
    if not value:
        raise PreventUpdate
    # if value is not No?ne:
    info = field_trial.list_all_sort_keys(value)
    info_global = key_utils.extract_sort_key_prefix(info)
    print(info_global[0])
    return info_global
    # return f"aoeuaoeu {value}"


@app.callback(
    Output('dropdown_info_sortkey', 'value'),
    Input('button_info_all', 'n_clicks'),
    Input('button_info_none', 'n_clicks'),
    State('dropdown_info_sortkey', 'options'),
)
def update_output(b1, b2, options):
    if not options:
        raise PreventUpdate
    if "button_info_all" == ctx.triggered_id:
        return options
    elif "button_info_none" == ctx.triggered_id:
        return None




@app.callback(
    Output("data_table", "columns"), Output("data_table", "data"),
    Output("dropdown_xaxis", "options"), Output("dropdown_yaxis", "options"),
    Input("fetch_data", "n_clicks"),
    State('select_trial', 'value'),
    State('dropdown_info_sortkey', 'value'),
)
def update_data_table(click, trial_id, info_list):
    if not trial_id:
        raise PreventUpdate
    print(trial_id)
    print(info_list)
    data = field_trial.get_by_trial_ids(trial_id, info_list)
    df = json_utils.result_list_to_df(data)
    # print(df)
    columns = [{"name": i, "id": i} for i in df.columns]
    return columns, df.to_dict('records'), df.columns, df.columns


@app.callback(
    Output("export_data", "data"),
    Input("btn_export", "n_clicks"),
    State("data_table", "data"),
    prevent_initial_call=True,
)
def export_dataframe(n_clicks, df):
    if not df:
        raise PreventUpdate
    df2 = pd.DataFrame(df)
    #  df.to_csv('df.csv', index=False, encoding='utf-8')
    # datetime
    return dcc.send_data_frame(df2.to_csv, filename="hello.csv")


@app.callback(
    Output('data_figure', 'figure'),
    Input('btn_plot', 'n_clicks'),
    State("data_table", "data"),
    State('dropdown_xaxis', 'value'), State('dropdown_yaxis', 'value'),
    State("raido-plot-type", "value"),
    prevent_initial_call=True,
    )
def update_figure(n_clicks, df, var_x, var_y, plot_type):
    # filtered_df = df[df.year == selected_year]
    if not var_x and not var_y:
        raise PreventUpdate
    df2 = pd.DataFrame(df)
    if plot_type == "Bar":
        fig = px.bar(df2, x=var_x, y=var_y)
    elif plot_type == "Line":
        fig = px.line(df2, x=var_x, y=var_y)
    elif plot_type == "Scatter":
        fig = px.scatter(df2, x=var_x, y=var_y)
        
    fig.update_layout(transition_duration=500)

    return fig

# @app.callback(
#     Output('dd-output-container', 'children'),
#     Input('demo-dropdown', 'value')
# )
# def update_output(value):
#     return f'You have selected {value}'

if __name__ == '__main__':
    app.run_server(debug=True)

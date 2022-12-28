# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.


import datetime
import io
import os

import dash
import numpy as np
import pandas as pd
import plotly.express as px
from dash import Dash, ctx, dash_table, dcc, html
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate

from dynamofield.db import dynamodb_init, init_db, key_utils, table_utils
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
    


@dash.callback(
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


@dash.callback(
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




@dash.callback(
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


@dash.callback(
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


@dash.callback(
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


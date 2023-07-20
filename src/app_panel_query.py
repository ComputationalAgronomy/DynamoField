import datetime
import io
import os

import dash
import dash_bootstrap_components as dbc
import numpy as np
import pandas as pd
import plotly.express as px
from dash import Dash, ctx, dash_table, dcc, html
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate

import app_style
import app_data
from dynamofield.db import dynamodb_init, init_db, key_utils, table_utils
from dynamofield.df import df_operation
from dynamofield.field import field_table, importer
from dynamofield.stats import summary_stats
from dynamofield.utils import json_utils

BTN_STYLE_ACTION = {  # "margin":"10px", 'margin-top': '20px',
    "width": "150px", "height": "60px",
    'align-items': 'center', 'justify-content': 'center',
    'font-size': "115%"
}

BTN_ACTION_CONF = {
    "size": "lg",
    "n_clicks": 0,
    "className": "m-2",
    "style": BTN_STYLE_ACTION
}


def trial_selection_panel():
    return html.Div(style={'padding': 10},
                    children=[
        dbc.Row([
            dbc.Col([
                dbc.Label('Select trial ID'),
                dcc.Dropdown(multi=True, id="select_trial"),
            ], width=3),
            dbc.Col([
                dbc.Label('Multi-Select Information related to this trial'),
                dcc.Dropdown(id="dropdown_info_sortkey", multi=True),
                dbc.Button('Select All', id='button_info_all', n_clicks=0,
                           size="lg", className="my-2"),  # style=app_style.btn_style),
                dbc.Button('Select None', id='button_info_none', n_clicks=0,
                           size="lg", className="m-2",
                           # style={"margin-left": "5px", "margin-top": "5px"}
                           ),
            ], width={"size": 4, "offset": 0.5}),
            dbc.Col([
                html.Br(),
                dbc.Button('Fetch data', id='btn_fetch_data',
                           **BTN_ACTION_CONF),
            ], width={"size": "auto", "offset": 1}),
        ]),
        dcc.Markdown(id="data_info"),
    ])


def merging_columns_within_info():
    return html.Div(style={'padding': 10},
                    children=[
        dbc.Row(html.H6("Merging columns within info tables")),
        dbc.Row([
            dbc.Col([
                dbc.Label('Info table'),
                dcc.Dropdown(id="dropdown_info_merge", multi=False),
                dbc.Label('Column names'),
                dcc.Dropdown(id="dropdown_info_merge_columns", multi=True),
            ], width={"size": 3}),
            # dbc.Col([
            #     dbc.Label('Second info table'),
            #     dcc.Dropdown(id="dropdown_info_sortkey_t2", multi=False),
            #     dbc.Label('Second table - Column name'),
            #     dcc.Dropdown(id="dropdown_info_t2_column", multi=False),
            # ], width={"size": 3, "offset": 0.5}),
            dbc.Col([
                html.Br(),
                dbc.Button('Merge columns', id='btn_merge_columns',
                           **BTN_ACTION_CONF)
            ], width={"size": "auto", "offset": 1})
        ]),
    ])


def merging_two_info():
    return html.Div(style={'padding': 10},
                    children=[
        dbc.Row(html.H6("Merging info tables")),
        dbc.Row([
            dbc.Col([
                dbc.Label('First info table'),
                dcc.Dropdown(id="dropdown_info_sortkey_t1", multi=False),
                dbc.Label('First table - Column name'),
                dcc.Dropdown(id="dropdown_info_t1_column", multi=False),
            ], width={"size": 3}),
            dbc.Col([
                dbc.Label('Second info table'),
                dcc.Dropdown(id="dropdown_info_sortkey_t2", multi=False),
                dbc.Label('Second table - Column name'),
                dcc.Dropdown(id="dropdown_info_t2_column", multi=False),
            ], width={"size": 3, "offset": 0.5}),
            dbc.Col([
                html.Br(),
                dbc.Button('Merge tables', id='btn_merge_info_tables',
                           **BTN_ACTION_CONF)
            ], width={"size": "auto", "offset": 1})
        ]),
    ])


def plot_stats_panel():
    return html.Div(style={'padding': 10},
                    children=[
        dbc.Row(html.H6("Plotting and statistical analysis.")),
        dbc.Row([
            dbc.Col([
                dcc.Markdown("**Factor\n: X-axis**"),
                dcc.Dropdown(id="dropdown_xaxis", multi=False),
            ], width=3),
            dbc.Col([
                dcc.Markdown("**Response: Y-axis**"),
                dcc.Dropdown(id="dropdown_yaxis", multi=False),
            ], width=3),
            dbc.Col([
                dcc.Markdown("\\[Optional\\] Slice by or Colour"),
                dcc.Dropdown(id="dropdown_by", multi=False),
            ], width=3),
            dbc.Col([
                dbc.Label("Plot type:"),
                dcc.RadioItems(options=["Scatter", "Line", "Bar"],
                    value="Scatter",
                    id="raido-plot-type",
                    inline=True,
                    style={"margin": 5, "padding": 5}
                ),
            ], width=2),
        ]),
        dbc.Row([
            dbc.Button("Plot data", id="btn_plot",
                       **BTN_ACTION_CONF),
            dbc.Button("Analysis", id="btn_stats",
                       **BTN_ACTION_CONF),
            dbc.Button("Summary", id="btn_summary",
                       **BTN_ACTION_CONF),
        ])
    ])


def generate_query_panel():
    return [html.Div(id="query_panel", style={'padding': 10},
                     children=[
        dcc.Store(id='store_data_table', storage_type='session',
                  clear_data=True),
        trial_selection_panel(),
        html.Hr(style={"height": "2px", "margin": "5px"}),

        dbc.Accordion([
            dbc.AccordionItem(
                children=merging_columns_within_info(),
                title="Merging columns within a data_type"),
            dbc.AccordionItem(
                children=merging_two_info(),
                title="Merging data_type"),
            dbc.AccordionItem(
                children=plot_stats_panel(),
                title="Stats"),
        ]),
        # merging_two_info(),
        # plot_stats_panel(),
        html.Hr(style={"height": "2px", "margin": "5px"}),

        html.H5("Statistical analysis"),
        dbc.Row([
            html.Pre(id="stats_output", title="Stats results",
                     style={"font-size": "125%"})
        ]),
        # html.Br(),
        # dbc.Button("Export data table (CSV)",
        #             id="btn_export",
        #             style=app_style.btn_style),
        # dcc.Download(id="export_data"),
        # html.Br(),

        html.H5("Table and figure"),
        dbc.Accordion([
            dbc.AccordionItem(
                title="Data table", item_id="item-table",
                children=[dash_table.DataTable(
                    id="data_table",
                    page_size=50,  # we have less data in this example, so setting to 20
                    style_table={
                        'height': '300px', 'overflowY': 'auto'},
                    export_format='csv')]
            ),
            dbc.AccordionItem(
                title="Figure", item_id="item-figure",
                children=dcc.Graph(id='data_figure'),)
        ],
            flush=True, always_open=True,
            active_item=["item-table", "item-figure"])


    ])]


@dash.callback(
    Output('select_trial', 'options'),
    Output('select_trial', 'disabled'),
    Input('tabs-function', 'value'),
    State('store_db_info', 'data'),
)
def get_id_list(tab, db_info):
    if tab != "tab-query" or db_info is None:
        raise PreventUpdate
    if not db_info["db_status"] or not db_info["table_status"]:
        print(f"Database offline")
        ids = [False]
        is_disabled = True
    else:
        # field_trial = init_field_trial(db_info["endpoint"], db_info["table_name"])
        field_trial = app_data.connect_db_table(db_info)
        ids = field_trial.get_all_trial_id()
        is_disabled = False
        # field_trial = init_field_trial(endpoint, table_name)
        # data = field_trial.get_by_trial_ids(trial_id, info_list)
    print(f"{ids}")
    return ids, is_disabled


@dash.callback(
    Output('dropdown_info_sortkey', 'options'),
    Input('select_trial', 'value'),
    State('store_db_info', 'data'),
)
def update_output_info(trial_ids, db_info):
    if not trial_ids:
        return []
    # if value is not None:
    field_trial = app_data.connect_db_table(db_info)
    info_global = set()
    for trial in trial_ids:
        info = field_trial.list_all_sort_keys(trial)
        info_set = key_utils.extract_sort_key_prefix(info)
        info_global.update(info_set)
        # print(info_global)
    info_global = list(info_global)
    info_global.sort()
    return info_global  # , info_global, info_global


@dash.callback(
    Output('dropdown_info_sortkey', 'value'),
    Input('button_info_all', 'n_clicks'),
    Input('button_info_none', 'n_clicks'),
    State('dropdown_info_sortkey', 'options'),
)
def update_info_selection_btn(b1, b2, options):
    if not options:
        raise PreventUpdate
    if "button_info_all" == ctx.triggered_id:
        return options
    elif "button_info_none" == ctx.triggered_id:
        return None


@dash.callback(
    Output("data_table", "data"),
    Input("store_data_table", "data"),
)
def update_output_table(store_table):
    return store_table


@dash.callback(
    # Output("data_table", "columns"),
    # Output("data_table", "data"),
    Output("store_data_table", "data"),
    Output('dropdown_info_sortkey_t1', 'options'),
    Output('dropdown_info_sortkey_t2', 'options'),
    Output("dropdown_xaxis", "options"),
    Output("dropdown_yaxis", "options"),
    Output("dropdown_by", "options"),
    Output("data_info", "children"),
    Input("btn_fetch_data", "n_clicks"),
    Input("btn_merge_info_tables", "n_clicks"),
    State('select_trial', 'value'),
    State('dropdown_info_sortkey', 'value'),
    State('dropdown_info_sortkey', 'options'),
    State('dropdown_info_sortkey_t1', 'value'),
    State('dropdown_info_sortkey_t2', 'value'),
    State("dropdown_info_t1_column", "value"),
    State("dropdown_info_t2_column", "value"),
    State("store_data_table", "data"),
    State('store_db_info', 'data'),

)
def update_data_table(b_fetch, b_merge,
                      trial_id, info_list, info_options,
                      info_t1, info_t2, t1_column, t2_column,
                      data_table, db_info):
    if not trial_id or not db_info["db_status"] or not db_info["table_status"]:
        raise PreventUpdate
    print(f"trial_id:{trial_id}")
    if "btn_fetch_data" == ctx.triggered_id:
        print(f"info_list:{info_list}\t{info_options}")
        if info_list is None:
            info_list = info_options
        field_trial = app_data.connect_db_table(db_info)
        data = field_trial.query_by_trial_ids(trial_id, info_list)
        df_output = json_utils.result_list_to_df(data)
    elif "btn_merge_info_tables" == ctx.triggered_id and data_table and t1_column and t2_column:
        print(f"column_select:{t1_column}\t{t2_column}")
        dd = pd.DataFrame(data_table)
        info_list = [info_t1, info_t2]
        df_output = df_operation.merge_df(dd, info_t1, info_t2,
                                          t1_column, t2_column)

    data_info = f"Data: {df_output.shape[0]} rows, {df_output.shape[1]} columns."
    output = [df_output.to_dict('records'),
              info_list, info_list,
              df_output.columns, df_output.columns, df_output.columns,
              data_info]
    return output


@dash.callback(
    Output("dropdown_info_t1_column", "options"),
    Output("dropdown_info_t2_column", "options"),
    Input('dropdown_info_sortkey_t1', 'value'),
    Input('dropdown_info_sortkey_t2', 'value'),
    State("data_table", "columns"),
    State("store_data_table", "data"),
)
def update_select_two_tables(info_1, info_2, columns, data_table):
    if not info_1 or not info_2:
        raise PreventUpdate
    # t1_c = None
    # t2_c = None
    print(f"info:{info_1}\t{info_2}")
    dd = pd.DataFrame(data_table)
    t1_c = df_operation.get_non_na_column_name(dd, info_1)
    t2_c = df_operation.get_non_na_column_name(dd, info_2)

    return t1_c, t2_c


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
    State("store_data_table", "data"),
    State('dropdown_xaxis', 'value'),
    State('dropdown_yaxis', 'value'),
    State('dropdown_by', 'value'),
    State("raido-plot-type", "value"),
    prevent_initial_call=True,
)
def update_figure(n_clicks, data_table, var_x, var_y, var_by, plot_type):
    # filtered_df = df[df.year == selected_year]
    if not var_x and not var_y:
        raise PreventUpdate
    df = pd.DataFrame(data_table)
    if plot_type == "Bar":
        fig = px.bar(df, x=var_x, y=var_y, color=var_by)
    elif plot_type == "Line":
        fig = px.line(df, x=var_x, y=var_y, color=var_by)
    elif plot_type == "Scatter":
        fig = px.scatter(df, x=var_x, y=var_y, color=var_by)

    fig.update_layout(transition_duration=500)

    return fig


@dash.callback(
    Output("stats_output", "children"),
    Input('btn_stats', 'n_clicks'),
    Input('btn_summary', 'n_clicks'),
    State("store_data_table", "data"),
    State('dropdown_xaxis', 'value'),
    State('dropdown_yaxis', 'value'),
    State('dropdown_by', 'value'),
    prevent_initial_call=True,
)
def stat_analysis(btn_stat, btn_summary, data_table,
                  var_x, var_y, var_by):
    if not var_x and not var_y:
        raise PreventUpdate
    df = pd.DataFrame(data_table)
    print(f"stats:{df.shape}\t{df.columns}\tVar:{var_x}, {var_y}, {var_by}")
    if "btn_stats" == ctx.triggered_id:
        results = summary_stats.analysis_design(
            df, factor=var_x, response=var_y, by=var_by)
    elif "btn_summary" == ctx.triggered_id:
        results = summary_stats.summary_table_df(
            df, factor=var_x, response=var_y, by=var_by)
    out = [f"Dataset:{k}\n{v}\n\n" for k, v in results.items()]
    output = "".join(out)
    stats_output = f"{output}"
    return stats_output

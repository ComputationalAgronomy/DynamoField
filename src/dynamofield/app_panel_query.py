
import dash
import dash_bootstrap_components as dbc
from dash import dash_table, dcc, html
from dynamofield import app_db, app_style


def trial_selection_panel():
    return html.Div(style={'padding': 10},
                    children=[
        dbc.Row([
            dbc.Col([
                dbc.Label('Select trial ID'),
                dcc.Dropdown(multi=True, id="dropdown_select_trial"),
                dbc.Button('Select All', id='button_trial_all',
                           **app_style.BTN_STD_CONF),
                dbc.Button('Select None', id='button_trial_none',
                           **app_style.BTN_STD_CONF),
            ], width=3),
            dbc.Col([
                dbc.Label('Multi-Select record_types related to this trial'),
                dcc.Dropdown(id="dropdown_info_sortkey", multi=True),
                dbc.Button('Select All', id='button_info_all',
                           **app_style.BTN_STD_CONF),
                dbc.Button('Select None', id='button_info_none',
                           **app_style.BTN_STD_CONF),
            ], width={"size": 4, "offset": 0.5}),
            dbc.Col([
                html.Br(),
                dbc.Button('Fetch data', id='btn_fetch_data',
                           **app_style.BTN_ACTION_CONF),
            ], width={"size": "auto", "offset": 1}),
        ]),
        dcc.Markdown(id="data_info"),
    ])


def merging_columns_within_info():
    return html.Div(style={'padding': 10},
                    children=[
        dbc.Row([
            dbc.Col([
                dbc.Label('Select a record_type'),
                dcc.Dropdown(id="dropdown_info_merge", multi=False),
            ], width={"size": 2}),
            dbc.Col([
                dbc.Label('Column names'),
                dcc.Dropdown(id="dropdown_info_merge_columns", multi=True),
                dbc.Label('New column name (Optional)'),
                dbc.Input(id="merge_new_col_name",
                          type="text", required=False,
                          minlength=3,
                          ),
            ], width={"size": 4, "offset": 0.5}),
            dbc.Col([
                html.Br(),
                dbc.Button('Merge columns', id='btn_merge_columns',
                           **app_style.BTN_ACTION_CONF)
            ], width={"size": "3", "offset": 0.5}),
            dbc.Col([
                html.Br(),
                dbc.Button('Replace existing record_type',
                           id='btn_replace_merged_columns',
                           color="warning",
                           **app_style.BTN_ACTION_CONF)
            ], width={"size": "3", "offset": 0.5})
        ]),
        dcc.Markdown(id="md_merge_info"),
    ])


def merging_two_info():
    return html.Div(style={'padding': 10},
                    children=[
        # dbc.Row(html.H6("Merging two record_types tables")),
        dbc.Row([
            dbc.Col([
                dbc.Label('First record_type table'),
                dcc.Dropdown(id="dropdown_info_sortkey_t1", multi=False),
                dbc.Label('First record_type - Column name'),
                dcc.Dropdown(id="dropdown_info_t1_column", multi=False),
            ], width={"size": 3}),
            dbc.Col([
                dbc.Label('Second record_type table'),
                dcc.Dropdown(id="dropdown_info_sortkey_t2", multi=False),
                dbc.Label('Second record_type - Column name'),
                dcc.Dropdown(id="dropdown_info_t2_column", multi=False),
            ], width={"size": 3, "offset": 0.5}),
            dbc.Col([
                html.Br(),
                dbc.Button('Merge tables', id='btn_merge_info_tables',
                           **app_style.BTN_ACTION_CONF)
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
                       **app_style.BTN_ACTION_CONF),
            dbc.Button("Analysis", id="btn_stats",
                       **app_style.BTN_ACTION_CONF),
            dbc.Button("Summary", id="btn_summary",
                       **app_style.BTN_ACTION_CONF),
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
                title="Merging columns within a record_type"),
            dbc.AccordionItem(
                children=merging_two_info(),
                title="Merging two record_types"),
            dbc.AccordionItem(
                children=plot_stats_panel(),
                title="Basic statistical analysis"),
        ], active_item=[]),
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
                children=dcc.Graph(id='data_figure'),
            )
        ],
            flush=True, always_open=True,
            active_item=["item-table", "item-figure"])
    ])]


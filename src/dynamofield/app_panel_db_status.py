import dash
import dash_bootstrap_components as dbc
from dash import dash_table, dcc, html
from dynamofield import app_db, app_style


def update_status_panel():
    return html.Div(children=[
        dcc.Markdown(id="db_markdown",
                     dangerously_allow_html=True),
        # dcc.RadioItems(id="radio_db_status",
        #                style={'display': 'flex', "margin-right": "5pt"},
        #                inline=False,
        #                options=[
        #     {'label': html.Div('DB Online', style={"color": "Green", "font-size": 16}), 'value': True}, #, 'disabled': True},
        #     {'label': html.Div(['DB Offline'], style={"color": "Red", "font-size": 16}), 'value': False},# , 'disabled': True},
        #     # {
        #     # "label": html.Div(['London'], style={'color': 'LightGreen', 'font-size': 20}),
        #     # "value": "London",
        # # },

        # ],),
    ],)


def update_config_panel():
    return html.Div(style={'padding': 10, 'margin': 5},
                    children=[
        dbc.Row(children=[
            html.H4("Connect to existing database:"),
            dbc.Col([
                # html.Div(className="three columns", children=[
                html.Label("Database endpoint:"),
                # html.Label("Default: http://localhost:8000/"),
                dbc.Input(id="db_endpoint", type="text", size="lg",
                          placeholder="http://localhost:8000/", debounce=True,
                          ),
                html.Label("Region selector:"),
                dbc.Select(id="db_regions", required=False, size="lg",
                        #    placeholder="local: http://localhost:8000/",
                           persistence=True
                           )
            ], width="4"),
            dbc.Col([
                # html.Div(className="three columns", children=[
                html.Label("DB table name:"),
                html.Label("Default: ft_db"),
                dcc.Input(id="db_table_name", type="text",
                          placeholder="ft_db", debounce=True,
                          ),
            ], width="auto"),
            dbc.Col([
                dbc.Button(  # className="three columns",
                    children='Connect Database', id='btn_connect_db',
                    **app_style.BTN_ACTION_CONF,
                ),
            ], width="auto"),
            dbc.Col([
                dbc.Button(id="btn_list_tables", children="List existing tables",
                    **app_style.BTN_ACTION_CONF,
                ),
            ], width="auto"),
        ])
    ])


def danger_delete_table_panel():
    return html.Div(style={'padding': 10},
                    children=[
        dbc.Card([
            dbc.CardHeader(
                html.H4("Danger Zone!",style={"color": "red"})),
            dbc.CardBody([
                dbc.Label("DELETE a table. Table name:"),
                dbc.Input(id="text_delete_tablename",
                          type="text", style={"width": "200px"}),
                dbc.Button(id="btn_delete_table", children="DELETE this table",
                           color="danger",
                           **app_style.BTN_ACTION_CONF,)
            ])
        ])
    ])


def create_new_table_panel():
    return html.Div(style={'padding': 10},
                    children=[
        dbc.Row([
            dbc.Col([
                html.H4("Database table information"),
                dbc.Label("Create a new table. Table name:"),
                dbc.Input(id="new_table_name", type="text", minLength=3),
                dbc.Button(id="btn_create_table", children="Create new table",
                           **app_style.BTN_ACTION_CONF,),
            ], width=3),
            dbc.Col([
                danger_delete_table_panel(),
            ], width={"size": 5, "offset": 2})
        ]),
        html.Br(),
        dcc.Markdown(id="db_table_md",
                     dangerously_allow_html=True),
        dash_table.DataTable(id="dt_list_table",
                             page_size=5,  # we have less data in this example, so setting to 20
                             style_table={'height': '150px', 'overflowY': 'auto', 'width': '300px'}),
    ])




def db_debug_panel():
    return html.Table([
        html.Thead([
            html.Tr(html.Th('DEBUG: Info stored in memory', colSpan="4")),
            # html.Tr([
            #     html.Th(html.Button('memory', id='memory-button')),
            #     html.Th(html.Button('localStorage', id='local-button')),
            #     html.Th(html.Button('sessionStorage', id='session-button'))
            # ]),
            html.Tr([
                    html.Th('Endpoint'),
                    html.Th('table_name'),
                    html.Th('DB status'),
                    html.Th('Table status')
                    ])
        ]),
        html.Tbody([
            html.Tr([
                    html.Td(id='data_endpoint'),
                    html.Td(id='data_table_name'),
                    html.Td(id='data_db_status'),
                    html.Td(id='data_table_status'),
                    ])
        ])
    ])


def generate_db_status_panel():


    return [
        # html.Div(#style={'padding': 10, 'flex': 1},
        #          children=[
        #     # html.Br(),
        #     html.Div(id="get_item_count_db"),
        # ]),
        dcc.Loading(
            id="loading-ep",
            type="default",
            children=html.Div(id="loading_update_db")
        ),
        # update_status_panel(),

        update_config_panel(),
        html.Hr(style={"height": "2px", "margin": "5px"}),
        create_new_table_panel(),

        html.Hr(style={"height": "2px", "margin": "5px"}),
        dbc.Button(id='btn_db_start', children='Start database (TODO)',
                   disabled=True,
                   **app_style.BTN_ACTION_CONF,
                   ),

        db_debug_panel(),


    ]


# @dash.callback(
#     Output("store_server", "data"),
#     Input("store_server", "data"),
# )
# def init_server(x):
#     dynamodb_server = init_dynamodb()
#     return dynamodb_server
#     #field_trial = init_field_trial(dynamodb_server)





# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.


import dash
import dash_bootstrap_components as dbc
from dash import Dash, dash_table, dcc, html
from dash.dependencies import ClientsideFunction, Input, Output, State

# from dash.exceptions import PreventUpdate
from dynamofield.app_panel_db_status import generate_db_status_panel
from dynamofield.app_panel_import import generate_import_panel
from dynamofield.app_panel_query import generate_query_panel
from dynamofield.callbacks import *

theme = dbc.themes.COSMO
external_stylesheets = [theme, "https://codepen.io/chriddyp/pen/bWLwgP.css"]

STORAGE_CLEAN_DATA = False

TAB_DEFAULT = 'tab-query'
# TAB_DEFAULT = 'tab-db-status'
TAB_DEFAULT = 'tab-import'


app = Dash(__name__,
    # use_pages=True,
    suppress_callback_exceptions=True,
    assets_folder='assetsX',
    external_stylesheets=external_stylesheets\
)


app.layout = html.Div(
    id="db",
    children=[
        # Banner
        html.Div(
            id="banner",
            className="banner",
            children=[
                html.H2("DynamoField - Field trial database"),
                dcc.Markdown(id="db_markdown",
                    dangerously_allow_html=True)
            ],
        ),

        dcc.Store(id='store_server', storage_type='local'),
        dcc.Store(id='store_table', storage_type='local'),

        dcc.Store(id='store_db_info', storage_type='session', clear_data=STORAGE_CLEAN_DATA),
        dcc.Tabs(id='tabs-function', value=TAB_DEFAULT, children=[
            dcc.Tab(label='Query database', value='tab-query'),
            dcc.Tab(label='Import data', value='tab-import'),
            dcc.Tab(label='Database Status', value='tab-db-status'),
        ]),
        html.Div(id='tabs-function-content'),
        html.Div(children=[
            dcc.Interval(id="refresh-graph-interval", disabled=False, interval=10000),
        ]),
    ]
)


@app.callback(
    Output('tabs-function-content', 'children'),
    Input('tabs-function', 'value')
)
def render_panels(tab):
    # print(tab)
    if tab == "tab-query":
        return generate_query_panel()
    elif tab == "tab-import":
        return generate_import_panel()
    elif tab == "tab-db-status":
        return generate_db_status_panel()

def main():
    app.run_server(debug=True)

if __name__ == '__main__':
    main()

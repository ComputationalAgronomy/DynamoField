
import dash
import numpy as np
import pandas as pd
from dash import Dash, ctx, dash_table, dcc, html
from dash.dependencies import ClientsideFunction, Input, Output, State
from dash.exceptions import PreventUpdate

from app_data import update_item_count


@dash.callback(
    Output('get_item_count', 'children'),
    Input('tabs-function', 'value')
)
def update_item_count_import(x):
    return update_item_count()


@dash.callback(
    Output('get_item_count_db', 'children'),
    Input('tabs-function', 'value')
)
def update_item_count_db(x):
    return update_item_count()
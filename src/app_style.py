
import base64
import datetime
# import field
import importlib
import io
import os
from datetime import datetime as dt

import boto3
import dash
import numpy as np
import pandas as pd
import plotly.express as px
from dash import Dash, ctx, dash_table, dcc, html
from dash.dependencies import ClientsideFunction, Input, Output, State
from dash.exceptions import PreventUpdate

from app_panel_import import *
from app_panel_query import *
from dynamofield.db import dynamodb_init, init_db, key_utils, table_utils
from dynamofield.field import field_table, importer
from dynamofield.utils import json_utils

btn_style = {
    # "margin-right": "0px",
    # "margin-left": "5px",
    "margin-top": "5px"
    # "margin": "5px"
}

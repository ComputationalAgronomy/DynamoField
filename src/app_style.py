
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
from app_panel_import import *
from app_panel_query import *


btn_style = {
    "margin-right": "25px",
    "margin-left": "1px",
    "margin-top": "5px"
}

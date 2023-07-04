import json
import logging
from decimal import Decimal

import boto3
import pandas as pd
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError

from dynamofield.utils import dict_utils, dynamo_utils, json_utils

# from dynamofield.field.field_table import FieldTable


# from io import BytesIO
# import os
# from pprint import pprint
# import requests
# from zipfile import ZipFile
# from question import Question


def create_db_key(key, value):
    return {key: f"{value}"}

def parse_key_condition(key, value, exact):
    if exact:
        sort_key_exprs = key.eq(value)
    else:
        sort_key_exprs = key.begins_with(value)
    return sort_key_exprs 


def find_offset_sort_key_list(sort_key):
    index = [int(s.rsplit("_")[1]) for s in sort_key]
    offset = max(index)
    return(offset)


def extract_sort_key_prefix(x):
    sort_keys_prefix = [s.rsplit("_")[0] for s in x]
    sort_keys_prefix = set(sort_keys_prefix)
    # offset = max(index)
    return(sort_keys_prefix)


def check_sort_keys(sort_keys):
    # if not isinstance(sort_keys, list) and len(sort_keys) > 0:
    if sort_keys is None or len(sort_keys) == 0:
        sort_keys = []
    if not isinstance(sort_keys, list):# and len(sort_keys) > 0:
        sort_keys = [sort_keys]
    return sort_keys
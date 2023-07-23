import importlib
from decimal import Decimal

import boto3
import numpy as np
import pandas as pd
import pytest

# from src.dynamofield.field import field_table
from dynamofield.db import db_keys

# from pandas.testing import assert_frame_equal




def test_check_sort_keys():
    sort_keys = []
    result = db_keys.check_sort_keys(sort_keys)
    expected = []
    assert result == expected

    sort_keys = None
    result = db_keys.check_sort_keys(sort_keys)
    expected = []
    assert result == expected

    sort_keys = ""
    result = db_keys.check_sort_keys(sort_keys)
    expected = []
    assert result == expected

    sort_keys = "aoeu"
    result = db_keys.check_sort_keys(sort_keys)
    expected = ["aoeu"]
    assert result == expected

    sort_keys = ["K1", "K2"]
    result = db_keys.check_sort_keys(sort_keys)
    expected = ["K1", "K2"]
    assert result == expected
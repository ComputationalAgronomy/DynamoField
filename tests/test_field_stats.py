import os
import pytest
import boto3
# import field
import importlib
import pandas as pd


from src.dynamofield.field import importer
from src.dynamofield import dynamodb_init
from src.dynamofield.field import field_table



# importlib.reload(field_table)
# importlib.reload(importer)

def _temp():
    table_name = "ft_db"
    dynamodb_res = dynamodb_init.init_dynamodb_resources()
    field_trial = field_table.FieldTable(dynamodb_res, table_name)


    trial_id = ["trial_3C", "trial_2B"]
    trial_id = "trial_3C"
    trial_id = "trial_2B"


    df_plots = field_trial.get_all_plots(trial_id)
    convert_float = ["yields", "meta"]
    for col in convert_float:
        df_plots[col] = df_plots[col].astype("float") 


    df_plots.describe()
    df_plots.info()

    df_plots.groupby("treatment").mean()

    df_trt = field_trial.get_all_treatments(trial_id)

    pd.merge(df_plots, df_trt, how="inner", on=["trial_id", "treatment"])


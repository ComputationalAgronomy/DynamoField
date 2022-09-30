import boto3
import importlib
import pandas as pd
from dynamofield.field import field_table

importlib.reload(field_table)



table_name = "ft_db"
dynamodb_res = dynamodb_init.init_dynamodb_resources()
field_trial = field_table.FieldTable(dynamodb_res, table_name)


trial_id = ["trial_3C", "trial_2B"]
trial_id = "trial_3C"
trial_id = "trial_2B"


field_trial.get_by_trial_id(trial_id)
field_trial.get_by_trial_id(trial_id=["trial_3C", "trial_2B"], sort_key="plot_0202") # TOFIX
field_trial.get_by_trial_id(trial_id="trial_3C", sort_key="plot_0202")
field_trial.get_by_trial_id(trial_id, sort_key="aoeu")


list_sort_key = field_trial.list_all_sort_keys(trial_id)


field_trial.list_all_sort_keys(trial_id, prune_common=True)
field_trial.get_all_non_standard_info(trial_id)


sort_key = "trial_meta"
sort_key = "trial_management"
field_trial.get_by_sort_key(sort_key, type="begins")

sort_key = "trial_contact"
field_trial.get_by_sort_key(sort_key)


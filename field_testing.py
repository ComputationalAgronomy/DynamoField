import boto3
import field
import importlib
import pandas as pd

importlib.reload(field)


importlib.reload(field)


field_trial = field.Field(dynamodb_res, table_name)


trial_id = ["trial_3C", "trial_2B"]
trial_id = "trial_3C"
trial_id = "trial_2B"


field_trial.get_by_trial_id(trial_id)
field_trial.get_by_trial_id(trial_id=["trial_3C", "trial_2B"], sort_key="plot_0202")
field_trial.get_by_trial_id(trial_id, sort_key="aoeu")


list_sort_key = field_trial.list_all_sort_keys(trial_id)



df_plots = field_trial.get_all_plots(trial_id)
convert_float = ["yield", "meta"]
for col in convert_float:
    df_plots[col] = df_plots[col].astype("float") 

df_plots.describe()
df_plots.info()

df_plots.groupby("treatment").mean()


df_trt = field_trial.get_all_treatments(trial_id)



pd.merge(df_plots, df_trt, how="inner", on=["trial_id", "treatment"])

list_sort_key = field_trial.list_all_sort_keys(trial_id)
field_trial.list_all_sort_keys(trial_id, prune_common=True)
field_trial.get_all_non_standard_info(trial_id)



sort_key = "trial_meta"
sort_key = "trial_management"
field_trial.get_by_sort_key(sort_key, type="begins")

sort_key = "trial_contact"
field_trial.get_by_sort_key(sort_key)


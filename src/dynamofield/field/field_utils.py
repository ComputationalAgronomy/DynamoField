import field
import importlib
import pandas as pd

importlib.reload(field)

# table_name = "ft_db"
# session = boto3.session.Session()
# dynamodb_res = session.resource('dynamodb', endpoint_url='http://localhost:8000')
# table = dynamodb_res.Table('ft_db')
# table.item_count

# trial_id = "trial_3C"
# ft = field.Field(dynamodb_res, table_name)

# results = ft.query_trial(trial_id)

def get_yield_trt(field, trial_id):
    # df = pd.read_json(json.dumps(results))
    df_plots = field.scan_plots(trial_id)
    df_trt = field.scan_treatments(trial_id)
    df_merged = pd.merge(df_plots, df_trt, how="inner", on=["trial_id", "treatment"])
    return df_merged


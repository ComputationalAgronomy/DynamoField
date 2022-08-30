import field
import importlib

importlib.reload(field)

table_name = "ft_db"


session = boto3.session.Session()
dynamodb_res = session.resource('dynamodb', endpoint_url='http://localhost:8000')
table = dynamodb_res.Table('ft_db')
table.item_count


ft = field.Field(dynamodb_res, table_name)
trial_id = ["trial_3C", "trial_2B"]
trial_id = "trial_3C"
trial_id = "trial_2B"


ft.query_trial(trial_id)
ft.query_trial(trial_id=["trial_3C", "trial_2B"], sort_key="plot_0202")
ft.query_trial(trial_id, sort_key="aoeu")


list_sort_key = ft.get_all_sort_keys(trial_id)



df_plots = ft.scan_plots(trial_id)
convert_float = ["yield", "meta"]
for col in convert_float:
    df_plots[col] = df_plots[col].astype("float") 

df_plots.describe()
df_plots.info()

df_plots.groupby("treatment").mean()


df_trt = ft.scan_treatments(trial_id)

pd.merge(df_plots, df_trt, how="inner", on=["trial_id", "treatment"])


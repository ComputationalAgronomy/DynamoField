import json
from decimal import Decimal
import pandas as pd


class DecimalEncoder(json.JSONEncoder):
    '''
    Usage: json.dumps(some_object, cls=DecimalEncoder)
    '''
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return json.JSONEncoder.default(self, obj)


def result_list_to_df(results) -> pd.DataFrame:
    # df_list = [pd.DataFrame.from_dict(r, orient='index') for r in results]
    # df = pd.concat(df_list, axis=1).transpose()
    df = pd.read_json(json.dumps(results, cls=DecimalEncoder))
    cols = list(df.columns.values)
    new_col = ['field_trial_id', 'data_type']
    try:
        [cols.remove(c) for c in new_col]
        new_col.extend(cols)
        df = df[new_col]
    except ValueError:
        pass

    return df


def reload_dynamo_json(data_dict):
    dynamo_json = json.loads(json.dumps(data_dict), parse_float=Decimal)
    return dynamo_json

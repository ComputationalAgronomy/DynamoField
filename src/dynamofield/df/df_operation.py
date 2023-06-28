
import pandas as pd

from dynamofield.field import field_table


def get_non_na_column_name(dd: pd.DataFrame, info) -> list:
    dsub = dd[dd["info"].str.startswith(f"{info}_")]
    dsub = dsub.dropna(axis=1, how='all')
    # d1 = pd.DataFrame()
    col_name = dsub.columns #.values.to_list()
    col_name = col_name.drop(field_table.FieldTable.PARTITION_KEY_NAME, errors="ignore") 
    col_name = col_name.drop(field_table.FieldTable.SORT_KEY_NAME, errors="ignore") 
    return col_name

def merge_df(dd: pd.DataFrame, info_t1, info_t2, t1_column, t2_column) -> pd.DataFrame:
    d1 = dd[dd["info"].str.startswith(f"{info_t1}_")].dropna(axis=1, how="all")
    d2 = dd[dd["info"].str.startswith(f"{info_t2}_")].dropna(axis=1, how="all")
    merge_name = t1_column
    print(f"{d1.columns}\n{d2.columns}\n")
    if t1_column != t2_column:
        #rename both d1 and d2
        merge_name = f"merge_{t1_column}_{t2_column}"
        d1 = d1.rename(columns={t1_column: merge_name})
        d2 = d2.rename(columns={t2_column: merge_name})
    df_merge = pd.merge(d1, d2, how="outer", 
                        on=[field_table.FieldTable.PARTITION_KEY_NAME, merge_name],
                        suffixes=["_t1", "_t2"])
    df_merge = df_merge.dropna(axis=1, how='all')
    return df_merge
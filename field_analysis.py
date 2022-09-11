import json
import logging
from decimal import Decimal
import utils.json_utils as json_utils

import statsmodels.api as sm
from statsmodels.formula.api import ols

# from field import Field


logger = logging.getLogger(__name__)



def summary_plots(field_trial, trial_id, response_list=["yield", "meta"]):
    df = field_trial.get_all_plots(trial_id)
    trt = df["treatment"]
    responses = df[response_list]

    df.groupby("treatment")["yield"].mean()
    subset = ["treatment", *response_list]
    agg_funcs = {response_list[0]: ['median', 'mean', 'std']}

    agg_funcs = {key: ['median', 'mean', 'std'] for key in response_list}
    summary_table = df.groupby("treatment").agg(agg_funcs)
    return summary_table



def analysis_design(df, factor="treatment", response_list=["yields", "meta"], block=None):
    anova_tables = []
    for response in response_list:
        df_subset = df[[factor, response]]
        formula = f"{response} ~ C({factor})"
        model = ols(formula, data=df_subset).fit()
        anova_result = sm.stats.anova_lm(model, typ=2)
        anova_tables.append(anova_result)
        
    return anova_tables
    


def parse_design(df):
    subdata = df[["info", "treatment"]]
    df["info"].replace("plot_(.*)", "\\1", regex=True)

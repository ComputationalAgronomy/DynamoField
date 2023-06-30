import json
import logging
from decimal import Decimal
# from typing_extensions import deprecated

import matplotlib.pyplot as plt
import scipy.stats as stats

import statsmodels.api as sm
import statsmodels.formula.api as smf
import statsmodels.stats.multicomp

class StatsAnalysis:
    def __init__(self, df, trial_id, response, block=None):
        self.df = df
        self.trial_id = trial_id
        self.response = response
        self.block = block
        # self.summary_table = summary_table_df(df, trial_id, response)
        # self.anova_table = analysis_design(self.summary_table, factor="treatment", response=response, block=block)
        # self.anova_table_df = self.anova_table.to_frame()
        # self.anova_table_df.reset_index(inplace=True)
        # self.anova_table_df.columns = ["treatment", *self.anova_table_df.columns]
        # self.anova_table_df.set_index("treatment", inplace=True)
        # self.anova_table_df.index.name = None

# from field import Field


def create_df_group(df, by=None):
    try:
        df_group = df.groupby(by)
    except TypeError:
        df_group = [("All", df)]
    return df_group


def summary_table_df(df, factor="treatment", response="yields", by=None):
    # agg_funcs = {response_list[0]: ['median', 'mean', 'std']}
    # agg_funcs = {key: ['median', 'mean', 'std'] for key in response_list}
    df_group = create_df_group(df, by)
    summary_output = {}
    for name, dd in df_group:
        summary = summary_table_single(dd, factor, response)
        summary_output[name] = summary
    return summary_output

def summary_table_single(df, factor="treatment", response="yields"):
    agg_funcs = {response: ['median', 'mean', 'std']}
    summary_table = df.groupby(factor).agg(agg_funcs)
    return summary_table


def summary_table_multi_responses(field_trial, trial_id, response_list=["yields"]):
    df = field_trial.get_all_plots(trial_id)
    trt = df["treatment"]
    responses = df[response_list]

    df.groupby("treatment")["yields"].mean()
    subset = ["treatment", *response_list]

    # agg_funcs = {response_list[0]: ['median', 'mean', 'std']}
    agg_funcs = {key: ['median', 'mean', 'std'] for key in response_list}
    summary_table = df.groupby("treatment").agg(agg_funcs)
    return summary_table




def _create_formula(response, factor, block=None):
    formula = f"{response} ~ C({factor})"
    if block is not None:
        formula = f"{formula} + C({block})"
    return formula



def analysis_design(df, factor="treatment", response="yields", block=None, by=None):
    df_group = create_df_group(df, by)
    summary_output = {}
    for name, dd in df_group:
        summary = analysis_design_single(dd, factor, response)
        summary_output[name] = summary
    return summary_output

def analysis_design_single(df, factor="treatment", response="yields", block=None):
    formula = _create_formula(response, factor, block)
    result = analysis_design_formula(df, formula)
    return result

def analysis_design_formula(df, formula):    
    model = smf.ols(formula, data=df).fit()
    anova_result = sm.stats.anova_lm(model, typ=2)
    return anova_result

# @deprecated
def analysis_design_multi_responses(df, factor="treatment", response_list=["yields", "meta"], block=None):
    anova_tables = {}
    for response in response_list:
        # df_subset = df[[factor, response]]
        formula = _create_formula(response, factor, block)
        model = smf.ols(formula, data=df).fit()
        anova_result = sm.stats.anova_lm(model, typ=2)
        anova_tables[response] = anova_result
    return anova_tables


# def analysis_rcbd(df, factor="treatment", block="block", response_list=["yields", "meta"]):
#     anova_tables = {}
#     for response in response_list:
#         model = ols(formula, data=df).fit()
#         anova_result_bf = sm.stats.anova_lm(model, typ=2)
#     # model = ols('value ~ C(Genotype) + C(years) + C(Genotype):C(years)', data=d_melt).fit()
#     # anova_table = sm.stats.anova_lm(model, typ=2)



def test_assumption(model):
    # res.anova_std_residuals are standardized residuals obtained from ANOVA (check above)
    sm.qqplot(model.resid, line='45')
    plt.xlabel("Theoretical Quantiles")
    plt.ylabel("Standardized Residuals")
    plt.show()
    # histogram
    plt.hist(model.resid, bins='auto', histtype='bar', ec='k') 
    plt.xlabel("Residuals")
    plt.ylabel('Frequency')
    plt.show()

    # Shapiro-Wilk test
    # w, pvalue = stats.shapiro(res.anova_model_out.resid)
    w, pvalue = stats.shapiro(model.resid)
    print(w, pvalue)




def tukey_single(df, factor="treatment", response="yield", block=None):
    
    m_comp = statsmodels.stats.multicomp.pairwise_tukeyhsd(df[response], groups=df[factor])
    return m_comp


def tukey(df, factor="treatment", response_list=["yields", "meta"], block=None):
    
    tukey_dict = {}
    for response in response_list:
        m_comp = tukey_single(df, factor, response)
        tukey_dict[response] = m_comp
    return tukey_dict

# @deprecated
def parse_design(df):
    subdata = df[["info", "treatment"]]
    df["info"].replace("plot_(.*)", "\\1", regex=True)



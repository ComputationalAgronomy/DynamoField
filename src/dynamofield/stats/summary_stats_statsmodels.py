import json
import logging
from decimal import Decimal

# import matplotlib.pyplot as plt
# import scipy.stats as stats

import statsmodels.api as sm
import statsmodels.formula.api as smf
import statsmodels.stats.multicomp


# from field import Field


# response_list=["yields", "meta"]

def summary_table(field_trial, trial_id, response_list=["yields"]):
    df = field_trial.get_all_plots(trial_id)
    trt = df["treatment"]
    responses = df[response_list]

    df.groupby("treatment")["yields"].mean()
    subset = ["treatment", *response_list]

    # agg_funcs = {response_list[0]: ['median', 'mean', 'std']}
    agg_funcs = {key: ['median', 'mean', 'std'] for key in response_list}
    summary_table = df.groupby("treatment").agg(agg_funcs)
    return summary_table


def create_formula(response, factor, block=None):
    formula = f"{response} ~ C({factor})"
    if block is not None:
        formula = f"{formula} + C({block})"
    return formula


def analysis_design(df, factor="treatment", response_list=["yields", "meta"], block=None):

    anova_tables = {}
    for response in response_list:
        # df_subset = df[[factor, response]]
        formula = create_formula(response, factor, block)
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



# def test_assumption(model):
    # res.anova_std_residuals are standardized residuals obtained from ANOVA (check above)
    # sm.qqplot(model.resid, line='45')
    # plt.xlabel("Theoretical Quantiles")
    # plt.ylabel("Standardized Residuals")
    # plt.show()
    # # histogram
    # plt.hist(model.resid, bins='auto', histtype='bar', ec='k')
    # plt.xlabel("Residuals")
    # plt.ylabel('Frequency')
    # plt.show()

    # Shapiro-Wilk test
    # w, pvalue = stats.shapiro(res.anova_model_out.resid)
    # w, pvalue = stats.shapiro(model.resid)
    # print(w, pvalue)



def tukey(df, factor="treatment", response_list=["yields", "meta"], block=None):

    tukey_dict = {}
    for response in response_list:
        # formula = f"{response} ~ C({factor})"
        m_comp = statsmodels.stats.multicomp.pairwise_tukeyhsd(df[response], groups=df[factor])
        tukey_dict[response] = m_comp
    return tukey_dict

def parse_design(df):
    subdata = df[['data_type', "treatment"]]
    df['data_type'].replace("plot_(.*)", "\\1", regex=True)


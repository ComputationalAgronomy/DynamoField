
import matplotlib.pyplot as plt
import seaborn as sns





def plot_data(df):
    ax = sns.boxplot(x='treatment', y='yields', data=df, color='#99c2a2')
    ax = sns.swarmplot(x="treatment", y="yields", data=df, color='#7d0013')
    plt.show()


def _anova_tukey(df, formula):
    # ANOVA table using bioinfokit v1.0.3 or later (it uses wrapper script for anova_lm)
    from bioinfokit.analys import stat
    res = stat()
    res.anova_stat(df=df, res_var='value', anova_model=formula)
    res.anova_summary
    # perform multiple pairwise comparison (Tukey's HSD)
    # unequal sample size data, tukey_hsd uses Tukey-Kramer test
    res = stat()
    res.tukey_hsd(df=df, res_var='yields', xfac_var='treatment', anova_model=formula)
    res.tukey_summary 
    # plt(res)
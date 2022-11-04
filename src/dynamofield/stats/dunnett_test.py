import numpy as np
from scipy.stats import norm
from scipy import integrate
from scipy.special import gamma
import pingouin as pg
# https://qiita.com/mosomoso_1910/items/1d28440d91f63829b6f9

def dunnett_two_side_unbalanced(data, dv, between,control):

  def dunnett_prob(T,v,lambda_params):

    def pdf(x):
      return norm.pdf(x)

    def cdf(x):
      return norm.cdf(x)

    def f(x,y):
      return pdf(y)*np.prod([cdf((lambda_i*y+T*x)/(np.sqrt(1-lambda_i**2)))-cdf((lambda_i*y-T*x)/(np.sqrt(1-lambda_i**2))) for lambda_i in lambda_params])

    def duv(x):
      return (v**(v/2)*x**(v-1)*np.exp(-v*x**2/2))/(gamma(v/2)*2**(v/2-1))

    def f_g(x,y):
      return f(x,y) * duv(x)

    return integrate.dblquad(f_g,-np.inf,np.inf,lambda x:0,lambda x:np.inf)[0]

  #First compute the ANOVA
  aov = pg.anova(dv=dv, data=data, between=between, detailed=True)
  v = aov.at[1, 'DF'] #自由度
  ng = aov.at[0, 'DF'] + 1 #全群数
  grp = data.groupby(between)[dv]
  n_sub = grp.count()
  control_index = n_sub.index.get_loc(control) #対照群のindexを取得
  n = n_sub.values #サンプル数
  gmeans = grp.mean().values#各平均
  gvar = aov.at[1, 'MS'] / n #各分散

  vs_g = np.delete(np.arange(ng),control_index) #対照群以外のindexを取得

  # Pairwise combinations（検定統計量Ｔを求める）
  mn = np.abs(gmeans[control_index]- gmeans[vs_g])
  se = np.sqrt(gvar[control_index] + gvar[vs_g]) #式は少し違うが等分散を仮定しているため
  tval = mn / se

  #lambdaを求める
  lambda_params = np.sqrt(n[vs_g]/(n[control_index]+n[vs_g]))

  pval = [1-dunnett_prob(t,v,lambda_params) for t in tval]

  stats = pd.DataFrame({
                      'A': [control]*len(vs_g),
                      'B': np.unique(data[between])[vs_g],
                      'mean(A)': np.round(gmeans[control_index], 3)*len(vs_g),
                      'mean(B)': np.round(gmeans[vs_g], 3),
                      'diff': np.round(mn, 3),
                      'se': np.round(se, 3),
                      'T': np.round(tval, 3),
                      'p-dunnett': pval
                      })
  return stats
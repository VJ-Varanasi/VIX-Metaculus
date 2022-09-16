import numpy as np
import pandas as pd
import glob
import datetime 
from scipy import stats
from sklearn.linear_model import Lasso
import statsmodels.api as sm
pd.options.mode.chained_assignment = None
from fastdtw import fastdtw
from scipy.spatial.distance import euclidean

print("")
return_scale = 1
#Autocorrelation lags
lags = 30



start_date = "2022-01-01"


d1_name ="Data/VIX_History*"
d2_name ="Data/2_Day_Smooth_Metaculus_Users_*"

d1_filename = glob.glob(d1_name)[0]
d2_filename = glob.glob(d2_name)[0]

d1= pd.read_csv(d1_filename)
d2= pd.read_csv(d2_filename)


d1["returns"] = d1["CLOSE"] - d1["CLOSE"].shift(return_scale)
d2["returns"] = d2.iloc[:,1] - d2.iloc[:,1].shift(return_scale)

d1=d1.dropna()
d2=d2.dropna()

d1.columns = d1.columns.str.upper()
d2.columns = d2.columns.str.upper()

d1_ret = d1[["DATE", "RETURNS"]]
d2_ret = d2[["DATE", "RETURNS"]]


d1_ret['DATE'] = pd.to_datetime(d1_ret["DATE"])
d1_ret['DATE']=d1_ret['DATE'].dt.strftime('%Y-%m-%d')



d1_ret = d1_ret.set_index("DATE")
d2_ret = d2_ret.set_index("DATE")

d1_ret = d1_ret.loc[start_date:]
d2_ret = d2_ret.loc[start_date:]

df = d1_ret.merge(d2_ret, on="DATE")


print("{}-day Return Correlations".format(return_scale))

print("Correlation Methods")
print("")
print("---------")
# Pearson Correlation
pearson = np.corrcoef(df["RETURNS_x"],df["RETURNS_y"] )[0][1]
print("Pearson Correlation: {}".format(pearson))

# Spearman Correlation
spearman = stats.spearmanr(df["RETURNS_x"],df["RETURNS_y"] )[0]
print("Spearman Correlation: {}".format(spearman))
print("---------")


cross_corr= sm.tsa.stattools.ccf(df["RETURNS_x"],df["RETURNS_y"] )
sorted_corr = sorted(np.abs(cross_corr), reverse = True) [0:5]


print("Cross Correlation")
for i in sorted_corr:
    if i in cross_corr:
        print("Lag {}: {}".format(cross_corr.tolist().index(i), i))
    else:
        print("Lag {}: -{}".format(cross_corr.tolist().index(-i), i))
print("---------")



print("Time Lagged Regression")



for i in range(1, lags):
    lag_name = "lag {}".format(i)
    df[lag_name] = df["RETURNS_y"].shift(i)

df = df.dropna()

Y = df["RETURNS_x"]
X = df.iloc[:,1:]
X2 = sm.add_constant(X)

est = sm.OLS(Y, X2)
est2 = est.fit()
print(est2.summary())

print("")
print("LASSO Regression")


X_norm = X.copy()
for i in X.columns:    
    X_norm[i] =(X[i] - X[i].mean()) / X[i].std() 

Y_norm = (Y - Y.mean()) / Y.std() 




alphas = np.geomspace(1e-3,1e-1, 20)
for i in alphas:
    # print("alpha = {}".format(i))
    # print("----")
    
    lassoreg = Lasso(alpha=i)
    lassoreg.fit(X_norm,Y_norm)
    coefs= lassoreg.coef_
    if sum(coefs) != 0:
        alpha = i
    # for j in range(len(coefs)):
    #     if j == 0:
    #         print("RETURNS_y: {}".format(coefs[j] ))
    #     else:
    #         print("Lag {}: {}".format(j, coefs[j] ))
        
    # print("")

print("alpha: {}".format(alpha))
lassoreg = Lasso(alpha=alpha)
lassoreg.fit(X_norm,Y_norm)
coefs= lassoreg.coef_


lasso_df = X_norm.copy()
drop_list = []
for i in range(len(coefs)):
    if coefs[i] == 0:
        drop_list.append(X_norm.columns[i])


lasso_df = lasso_df.drop(columns = drop_list)

lasso2 = sm.add_constant(lasso_df)
sparse_reg = sm.OLS(Y, lasso2)
sparse = sparse_reg.fit()
print(sparse.summary())

print("Granger Causality")

#test for stationarity

adf1 = sm.tsa.stattools.adfuller(df["RETURNS_x"], autolag='AIC')[1]
print(adf1)

adf2 = sm.tsa.stattools.adfuller(df["RETURNS_y"], autolag='AIC')[1]
print(adf2)

if adf1 < 0.05 and adf2 < 0.05:
    granger = sm.tsa.stattools.grangercausalitytests(df[["RETURNS_x","RETURNS_y"]], lags)

print("---------------------")
print("Dynamic Time Wrapping")


dtw1 = (d1_ret["RETURNS"] - d1_ret["RETURNS"].mean())/d1_ret["RETURNS"].std() 
dtw2 = (d2_ret["RETURNS"] - d2_ret["RETURNS"].mean())/d2_ret["RETURNS"].std() 

distance, path = fastdtw( dtw1,dtw2, dist=euclidean)
print("Distance: {}".format(distance))
print("Average Distance: {}".format(distance/len(dtw2)))
print("---------------------")

from time import strftime
from tkinter import N
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import glob
from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.tsa.stattools import adfuller
from pandas.plotting import autocorrelation_plot
import datetime 

import re
import matplotlib.ticker as ticker
import matplotlib.dates as mdates

data_name ="VIX"
start_date ="2022-01-01"
remove_spike = 0
smooth_data = 0
percent_cutoff = 0.1



remove_date ="01/03/2022"

activity = pd.read_csv("Data/visitors-actives.csv")

activity["Day Index"]= pd.to_datetime(activity["Day Index"]).dt.strftime('%m/%d/%Y')
activity = activity.rename(columns = {"Day Index" : "DATE", "1 Day Active Users": "Users"})
activity = activity.replace(',','',regex=True)
activity["Users"] = pd.to_numeric(activity["Users"])
if(remove_spike == 1):
    activity['DATE']
    index_val = activity.index[activity["DATE"]==remove_date][0]
    activity.loc[index_val,"Users"] = (int(activity.at[index_val + 1,"Users"]) + int(activity.at[index_val - 1,"Users"]))/2

activity["DATE"] =pd.to_datetime(activity["DATE"])
#activity = activity.loc[start_date:]

print(activity.tail(97))



""" 
scale = 1
n = len(activity["Users"])


new_col = [0] * n
for i in range(n):
    if(i < scale):
                new_col[i] = activity.at[i,"DATE"].strftime('%Y-%m-%d')
    else:
        percent_diff = (activity.at[i,"Users"] - activity.at[i-scale,"Users"]) /activity.at[i-scale,"Users"]
        if(percent_diff <= 0):
            gamma = 0
        else:
            gamma = 10* percent_diff
        new_col[i] = (activity.at[i,"DATE"] +datetime.timedelta(gamma)) .strftime('%Y-%m-%d')
activity["New_Date"] = new_col 


# partial_name = f'Data/{data_name}_History*'
# filename = glob.glob(partial_name)[0]
# vix_data= pd.read_csv(filename, parse_dates=['DATE'], index_col = ['DATE'])
# vix_data = vix_data.loc[start_date:]
# vix_data.index = vix_data.index.strftime('%m/%d/%Y')


# vix_data = vix_data.drop(columns = ["OPEN", "HIGH", "LOW"])
    

# df = vix_data.merge(activity, how= 'inner', on = 'DATE')

# df["Users"] = pd.to_numeric(df["Users"])
#df=df.set_index("DATE")

fig, ax1 = plt.subplots()

color = 'tab:orange'
ax1.set_xlabel('Date')
ax1.set_ylabel('Actual', color=color)
ax1.plot(activity["DATE"], activity["Users"], color=color)

ax1.xaxis.set_major_locator(mdates.MonthLocator())

ax2 = ax1.twiny()  # instantiate a second axes that shares the same x-axis

color = 'tab:green'
ax2.set_ylabel('Adjusted', color=color)  # we already handled the x-label with ax1
ax2.plot(activity["New_Date"], activity["Users"], color=color)
ax2.tick_params(axis='y', labelcolor=color)

fig.tight_layout()  # otherwise the right y-label is slightly clipped
plt.title("Actual and Adjusted Metaculus User Activity")
plt.show() """
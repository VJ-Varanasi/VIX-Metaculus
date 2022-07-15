""" #Files
from bs4 import BeautifulSoup
from urllib.request import urlopen
#import requests


#Opening Pages
my_url = "https://en.wikipedia.org/wiki/Who_Wants_to_Be_a_Millionaire_(American_game_show)"
#my_url = "http://olympus.realpython.org/profiles/aphrodite"
url_client = urlopen(my_url)
#url_client = requests.get(my_url)
page_html = url_client.read()
url_client.close()

#html = page_html.decode("utf-8")
#print(html) 

#Parsing HTML
page_soup = BeautifulSoup(page_html, "html.parser")
print(page_soup.h1)
print(page_soup.p)

h2s = page_soup.findAll("h2") """

import pandas as pd
from statsmodels.tsa.stattools import grangercausalitytests
import re
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import matplotlib.dates as mdates

activity = pd.read_csv("Data/visitors-actives.csv")
vix_data = pd.read_csv("Data/VIX_History_2022-04-16.csv")

vix_data["DATE"]= pd.to_datetime(vix_data["DATE"]).dt.strftime('%m/%d/%Y')
activity["Day Index"]= pd.to_datetime(activity["Day Index"]).dt.strftime('%m/%d/%Y')
activity = activity.rename(columns = {"Day Index" : "DATE", "1 Day Active Users": "Users"})
vix_data = vix_data.drop(columns = ["OPEN", "HIGH", "LOW"])

activity = activity.replace(',','',regex=True)
#activity["Users"] = pd.to_numeric(activity["Users"])
#print(activity.tail())
#print(vix_data.tail())

#merge_data = pd.merge_asof(activity, vix_data, on = "DATE")
merge_data = vix_data.merge(activity, how= 'inner', on = 'DATE')
#print(merge_data.tail(n= 75))


#grangercausalitytests(merge_data[['Users', 'CLOSE']].tail(n = 75), maxlag=[23])



df=merge_data.tail(n=75)
df["Users"] = pd.to_numeric(df["Users"])
df=df.set_index("DATE")

#print(df)
X= df.index




fig, ax1 = plt.subplots()

#tick_spacing = 1
color = 'tab:blue'
ax1.set_xlabel('Date')
ax1.set_ylabel('VIX Index', color=color)
ax1.plot(X, df["CLOSE"], color=color)

ax1.xaxis.set_major_locator(mdates.MonthLocator())
#ax1.xaxis.set_major_formatter(
   # mdates.ConciseDateFormatter(ax1.xaxis.get_major_locator()))


#ax1.xaxis.set_major_locator(ticker.MultipleLocator(tick_spacing))
#ax1.locator_params(axis="x", nbins=3)
ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis

color = 'tab:orange'
ax2.set_ylabel('User Activity', color=color)  # we already handled the x-label with ax1
ax2.plot(X,df["Users"], color=color)
ax2.tick_params(axis='y', labelcolor=color)
#ax2.locator_params(axis="x", nbins=3)



#fig.title("VIX Index and Metaculus User Activity")
fig.tight_layout()  # otherwise the right y-label is slightly clipped
plt.title("VIX Index and Metaculus User Activity")

plt.show()
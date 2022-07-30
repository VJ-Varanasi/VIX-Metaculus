from pickle import FALSE, TRUE
import backtrader as bt
import pandas as pd
import datetime
import yfinance as yf
import matplotlib.dates
import glob


# Defining Class for VXX CSV Data
class VXX_DATA(bt.feeds.GenericCSVData):
    params =  (
        ("nullvalue", 0.0),
        ("dtformat", ('%Y-%m-%d')),
         ("datetime", 1),
        ("time", -1),
        ("high", 3),
        ("low",4),
        ("open", 2),
        ("close",5),
        ("volume", 7),
        ("openinterest",-1)
    )

# Defining Class for Metaculus User Data
class METACULUS_DATA(bt.feeds.GenericCSVData):
    params =  (
        ("nullvalue", 0.0),
        ("dtformat", ('%m/%d/%Y')),
         ("datetime", 0),
        ("time", -1),
        ("high", -1),
        ("low",-1),
        ("open", -1),
        ("close",1),
        ("volume", -1),
        ("openinterest",-1)
    )

#Add Optimization Param
cerebro = bt.Cerebro(optreturn= False)

#Define Start and End Dates
start = datetime.datetime(2020, 1, 1)
end = datetime.datetime(2022, 1, 1)

#Get File Name
partial_name = f'Data/VXX_History*'
filename = glob.glob(partial_name)[0]

#Metaculus filename
metaculus_filename = 'Data/visitors-actives.csv'


yeet = pd.read_csv(metaculus_filename)
print(yeet.head())
print(yeet.info())
yeet['Day Index'] = pd.to_datetime(yeet['Day Index'], format = '%m/%d/%y')
print(yeet.head())
print(yeet.info())

#Add data to cerebro
feed1 = VXX_DATA(dataname = filename, fromdate = start, todate = end)
feed2 = METACULUS_DATA(dataname = metaculus_filename, fromdate = start, todate = end)
cerebro.adddata(feed1)
#cerebro.adddata(feed2)


cerebro.run()

cerebro.plot(stdstats=False)
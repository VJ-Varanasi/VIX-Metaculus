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
        ("dtformat", ('%Y-%m-%d')),
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
end = datetime.datetime(2022, 4, 1)

#Get File Name
partial_name = f'Data/VXX_History*'
filename = glob.glob(partial_name)[0]

#Metaculus filename
#Controls which smoothness level to use
smooth_level = 2

metaculus_partial_name = "Data/{}_Day_Smooth_Metaculus_Users_*".format(smooth_level)
metaculus_filename = glob.glob(metaculus_partial_name)[0]


#Add data to cerebro
feed1 = VXX_DATA(dataname = filename, fromdate = start, todate = end)
feed2 = METACULUS_DATA(dataname = metaculus_filename, fromdate = start, todate = end)
cerebro.adddata(feed1)

feed2.compensate(feed1)
feed2.plotinfo.plotmaster = feed1
#feed2.plotinfo.sameaxis = True
cerebro.adddata(feed2)



cerebro.run(stdstats=False)

cerebro.plot()
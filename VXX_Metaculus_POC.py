from pickle import FALSE, TRUE
import backtrader as bt
import pandas as pd
import datetime
import yfinance as yf
import glob
import trading_strat
import statsmodels.api as sm
import numpy as np
import statistics

# Defining Class for VXX CSV Data
class YF_DATA(bt.feeds.GenericCSVData):
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


strat = trading_strat.Metaculus_lead_SPY
trading_sec = 'SPY'


#Define Start and End Dates
start = datetime.datetime(2020, 1, 1)
end = datetime.datetime(2022, 4, 1)
delta = end - start


#Add Optimization Param
cerebro = bt.Cerebro(stdstats=True)

#Get File Name
vxx_partial_name = f'Data/VXX_History*'
vxx_filename = glob.glob(vxx_partial_name)[0]

spy_partial_name = f'Data/SPY_History*'
spy_filename = glob.glob(spy_partial_name)[0]

#Metaculus filename
#Controls which smoothness level to use
smooth_level = 2

metaculus_partial_name = "Data/{}_Day_Smooth_Metaculus_Users_*".format(smooth_level)
metaculus_filename = glob.glob(metaculus_partial_name)[0]

#Read Data in
meta_feed = METACULUS_DATA(dataname = metaculus_filename, fromdate = start, todate = end)

#Add data to cerebro - Add data you are trading first
if trading_sec == "SPY":
    spy_feed = YF_DATA(dataname = spy_filename, fromdate = start, todate = end)
    cerebro.adddata(spy_feed)
    meta_feed.compensate(spy_feed)  # let the system know ops on data1 affect data0
    meta_feed.plotinfo.plotmaster = spy_feed
    

elif trading_sec == "VXX":
    vxx_feed = YF_DATA(dataname = vxx_filename, fromdate = start, todate = end)
    cerebro.adddata(vxx_feed)
    meta_feed.compensate(vxx_feed)  # let the system know ops on data1 affect data0
    meta_feed.plotinfo.plotmaster = vxx_feed
   


cerebro.adddata(meta_feed)

#Add Strat
cerebro.addstrategy(strat)

cerebro.addobserver(bt.observers.Broker)

cerebro.addobserver(bt.observers.BuySell)

#Add Sharpe Ratio
#Default risk free interest rate of 1%
cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name = 'sharpe_ratio')


#Default position size
cerebro.addsizer(bt.sizers.SizerFix, stake=1)

#Initial Val
start_portfolio_value = cerebro.broker.getvalue()

#Run Cerebro
run = cerebro.run(stdstats=False)



#Final Log
end_portfolio_value = cerebro.broker.getvalue()
pnl = end_portfolio_value - start_portfolio_value
sharpe = run[0].analyzers.sharpe_ratio.get_analysis()['sharperatio']
percent_underwater = round(run[0].underwater/delta.days,2)*100
print(trading_sec)
print('---------------')
print(f'Starting Portfolio Value: {start_portfolio_value:2f}')
print(f'Final Portfolio Value: {end_portfolio_value:2f}')
print(f'PnL: ${pnl:.2f}')
print(f'Sharpe Ratio: {sharpe}')
print(f'Percent Underwater: {percent_underwater}%')
print('---------------')

#Plotting
cerebro.plot(volume= False,plotdist = 1)



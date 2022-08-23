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


strat = trading_strat.Metaculus_lead
trading_sec = 'VXX'


#Define Start and End Dates
start = datetime.datetime(2020, 1, 1)
end = datetime.datetime(2022, 4, 1)



#Add Optimization Param
cerebro = bt.Cerebro(optreturn = False)

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
    #meta_feed.compensate(spy_feed)  # let the system know ops on data1 affect data0
    #meta_feed.plotinfo.plotmaster = spy_feed
    #meta_feed.plotinfo.sameaxis = True

elif trading_sec == "VXX":
    vxx_feed = YF_DATA(dataname = vxx_filename, fromdate = start, todate = end)
    cerebro.adddata(vxx_feed)
    #meta_feed.compensate(vxx_feed)  # let the system know ops on data1 affect data0
    #meta_feed.plotinfo.plotmaster = vxx_feed
    #meta_feed.plotinfo.sameaxis = True


cerebro.adddata(meta_feed)


#OPTIMIZATION SECTION

#Add Strat
cerebro.optstrategy(strat, lead =range(0,30), pct_chng = np.linspace(0,1,11), range = 5)
#cerebro.optstrategy(strat, pfast =range(5,7), pslow = range (50,53), lag = range (5,7))

#Add Sharpe Ratio
cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name = 'sharpe_ratio')



#Run Optimixation
#Add Optimization Param

if __name__ == '__main__':
    optimized_runs = cerebro.run(stdstats = False)
    #Pull Results
    final_results_list = []
    for run in optimized_runs:
        for strategy in run:
            PnL = round(strategy.broker.get_value() - 10000,2)
            sharpe = strategy.analyzers.sharpe_ratio.get_analysis()
            final_results_list.append([strategy.params.lead, strategy.params.pct_chng, PnL, sharpe['sharperatio']])
            #final_results_list.append([strategy.params.pfast, strategy.params.pslow, strategy.params.lag, PnL, sharpe['sharperatio']])

    #Sort Results
    sort_by_sharpe = sorted(final_results_list, key=lambda x: x[2], reverse=True)

    #Print Results
    for line in sort_by_sharpe[:5]:
        print(line)

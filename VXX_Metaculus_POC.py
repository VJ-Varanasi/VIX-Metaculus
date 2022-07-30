from pickle import FALSE, TRUE
import backtrader as bt
import pandas as pd
import datetime
import yfinance as yf
import matplotlib.dates
import glob


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

class VXX_Strat(bt.Strategy):
    # Always define parameters first
    def __init__(self):

        self.vxx = self.data0.close
        self.meta=self.data1.close
        self.spy = self.data2.close

    # Trading logic second
    def next(self):
        if not self.position:
            if self.meta[-1] < self.meta[0]:
                self.log(f'BUY CREATE {self.vxx[0]:2f}, Metaculus: {self.meta[0]},{self.meta[-1]} ')
                self.buy()
        elif self.meta[-1] > self.meta[0]:
            self.log(f'CLOSE CREATE {self.vxx[0]:2f}, Metaculus: {self.meta[0]},{self.meta[-1]}')
            self.close()

    def log (self, txt, dt = None):
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))




#Add Optimization Param
cerebro = bt.Cerebro(optreturn= False)

#Define Start and End Dates
start = datetime.datetime(2020, 1, 1)
end = datetime.datetime(2022, 4, 1)

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


#Add data to cerebro
feed1 = YF_DATA(dataname = vxx_filename, fromdate = start, todate = end)
feed2 = METACULUS_DATA(dataname = metaculus_filename, fromdate = start, todate = end)
feed3 = YF_DATA(dataname = spy_filename, fromdate = start, todate = end)
cerebro.adddata(feed1)
cerebro.adddata(feed2)
cerebro.adddata(feed3)



#Add Strat
cerebro.addstrategy(VXX_Strat)


#Default position size
cerebro.addsizer(bt.sizers.SizerFix, stake=3)

#Initial Val
start_portfolio_value = cerebro.broker.getvalue()

cerebro.run(stdstats=False)

#cerebro.plot()

#Final Log
end_portfolio_value = cerebro.broker.getvalue()
pnl = end_portfolio_value - start_portfolio_value
print(f'Starting Portfolio Value: {start_portfolio_value:2f}')
print(f'Final Portfolio Value: {end_portfolio_value:2f}')
print(f'PnL: {pnl:.2f}')

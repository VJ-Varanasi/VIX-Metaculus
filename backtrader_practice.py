#from fcntl import F_SEAL_SEAL
from pickle import FALSE, TRUE
import backtrader as bt
import pandas as pd
import datetime
import yfinance as yf
import matplotlib.dates
import glob

#Reference: https://algotrading101.com/learn/backtrader-for-backtesting/#:~:text=If%20you%20want%20to%20backtest,stored%20on%20your%20local%20computer.

#import collections

#try:
#    collectionsAbc = collections.abc
#except AttributeError:
#    collectionsAbc = collections


# Defining Class for VXX CSV Data
class MyHLOC(bt.feeds.GenericCSVData):
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

# Defining Trading Strategies
class MyStrategy(bt.Strategy):
    # Always define parameters first
    def __init__(self):
        sma1 = bt.ind.SMA(period = 50)
        sma2 = bt.ind.SMA(period = 100)
        self.crossover = bt.ind.CrossOver(sma1,sma2)
    
    # Trading logic second
    def next(self):
        if not self.position:
            if self.crossover < 0:
                self.buy()
        elif self.crossover > 0:
            self.close()

class PrintClose(bt.Strategy):

    def log(self, txt, dt=None):
        ''' Logging function for this strategy'''
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        # Keep a reference to the "close" line in the data[0] dataseries
        self.dataclose = self.datas[0].close

    def next(self):
        # Simply log the closing price of the series from the reference
        self.log('Close, %.2f' % self.dataclose[0])

#With Logs
class MAcrossover(bt.Strategy):
    #moving average parameters
    params = (("pfast", 18), ("pslow", 52),)
    
    def log (self, txt, dt = None):
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))
    
    def __init__(self):
        self.dataclose = self.datas[0].close
        self.order = None
        
        self.slow_sma = bt.indicators.MovingAverageSimple(self.datas[0], period=self.params.pslow)
        self.fast_sma = bt.indicators.MovingAverageSimple(self.datas[0], period=self.params.pfast)

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return

        if order.status in [order.Completed]:
            #log if buy
            if order.isbuy():
                self.log(f'BUY EXECUTED, {order.executed.price:.2f}')
            #log if sell
            elif order.issell():
                self.log(f'SELL EXECUTED, {order.executed.price:.2f}')
            self.bar_executed = len(self)
            
        #Log if order didnt go through
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')
            
        #reset order
        self.order = None
    
    def next(self):
        print(cerebro.broker.getvalue())
        #check for open orders (limit to one trade at a time)
        if self.order:
            return

        #Check existing positions in market
        if not self.position:
            #Not in market so look for Open Trades
            
            if self.fast_sma[0] > self.slow_sma[0] and self.fast_sma[-1] < self.slow_sma[-1]:
                self.log(f'BUY CREATE {self.dataclose[0]:2f}')
                self.order = self.buy()
            elif self.fast_sma[0] < self.slow_sma[0] and self.fast_sma[-1] > self.slow_sma[-1]:
                self.log(f'SELL CREATE {self.dataclose[0]:2f}')
                self.order = self.sell()
        else:
            #In market so look to Close Trades
            
            #Exit after 5 bars
            if len(self) >= (self.bar_executed + 5):
                self.log(f'CLOSE CREATE {self.dataclose[0]:2f}')
                self.order = self.close()

#Used for optimization
class MAcrossover_opt(bt.Strategy):
    #moving average parameters
    params = (("pfast", 20), ("pslow", 50),)
    
    def log (self, txt, dt = None):
        dt = dt or self.datas[0].datetime.date(0)
        #print('%s, %s' % (dt.isoformat(), txt))
    
    def __init__(self):
        self.dataclose = self.datas[0].close
        self.order = None
        
        self.slow_sma = bt.indicators.MovingAverageSimple(self.datas[0], period=self.params.pslow)
        self.fast_sma = bt.indicators.MovingAverageSimple(self.datas[0], period=self.params.pfast)

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return

        if order.status in [order.Completed]:
            #log if buy
            if order.isbuy():
                self.log(f'BUY EXECUTED, {order.executed.price:.2f}')
            #log if sell
            elif order.issell():
                self.log(f'SELL EXECUTED, {order.executed.price:.2f}')
            self.bar_executed = len(self)
            
        #Log if order didnt go through
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')
            
        #reset order
        self.order = None
    
    def next(self):
        #check for open orders (limit to one trade at a time)
        if self.order:
            return

        #Check existing positions in market
        if not self.position:
            #Not in market so look for Open Trades
            
            if self.fast_sma[0] > self.slow_sma[0] and self.fast_sma[-1] < self.slow_sma[-1]:
                self.log(f'BUY CREATE {self.dataclose[0]:2f}')
                self.order = self.buy()
            elif self.fast_sma[0] < self.slow_sma[0] and self.fast_sma[-1] > self.slow_sma[-1]:
                self.log(f'SELL CREATE {self.dataclose[0]:2f}')
                self.order = self.sell()
        else:
            #In market so look to Close Trades
            
            #Exit after 5 bars
            if len(self) >= (self.bar_executed + 5):
                self.log(f'CLOSE CREATE {self.dataclose[0]:2f}')
                self.order = self.close()

#Instantiate Cerebro engine

#Add Optimization Param
cerebro = bt.Cerebro(optreturn= False)

#Define Start and End Dates
start = datetime.datetime(2021, 1, 1)
end = datetime.datetime(2022, 4, 1)


#Get File Name
partial_name = f'Data/VXX_History*'
filename = glob.glob(partial_name)[0]

#Add data to cerebro
feed = MyHLOC(dataname = filename, fromdate = start, todate = end)
cerebro.adddata(feed)

#Add strategey
cerebro.addstrategy(MAcrossover)
#cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name = 'sharpe_ratio')
#cerebro.optstrategy(MAcrossover_opt, pfast =range(5,20), pslow = range (50,100))

#Add sizer (portion of portfolio traded)
#cerebro.addsizer(bt.sizers.PercentSizer, percents = 50)

#To add an indicator, simply code up a new class and add it to the next funciton

# Add Analyzer
#cerebro.addanalyzer(bt.analyzers.AnnualReturn, _name="areturn")

#Default position size
cerebro.addsizer(bt.sizers.SizerFix, stake=3)

#Initial Val
start_portfolio_value = cerebro.broker.getvalue()


#Run Optimixation
# if __name__ == '__main__':
#     optimized_runs = cerebro.run()

#     #Pull Results
#     final_results_list = []
#     for run in optimized_runs:
#         for strategy in run:
#             PnL = round(strategy.broker.get_value() - 10000,2)
#             sharpe = strategy.analyzers.sharpe_ratio.get_analysis()
#             final_results_list.append([strategy.params.pfast, strategy.params.pslow, PnL, sharpe['sharperatio']])

#     #Sort Results
#     sort_by_sharpe = sorted(final_results_list, key=lambda x: x[2], reverse=True)

#     #Print Results
#     for line in sort_by_sharpe[:5]:
#         print(line)

#Run Normal Cerebro
cerebro.run()

#Final Log
end_portfolio_value = cerebro.broker.getvalue()
pnl = end_portfolio_value - start_portfolio_value
print(f'Starting Portfolio Value: {start_portfolio_value:2f}')
print(f'Final Portfolio Value: {end_portfolio_value:2f}')
print(f'PnL: {pnl:.2f}')


#Plot
#cerebro.plot(stdstats=False)

#print(teststrat[0].analyzers.areturn.get_analysis())
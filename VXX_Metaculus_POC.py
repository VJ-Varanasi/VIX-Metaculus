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

class Metaculus_Momentum(bt.Strategy):
    # Always define parameters first
    def __init__(self):
        self.order = None
        self.data = self.data0.close
        self.meta=self.data1.close
        self.buy_counter = 0
        self.sell_counter = 0


    # Trading logic second
    def next(self):
        if self.order:
            return

        if not self.position:
            if self.meta[-1] < self.meta[0]:
                self.log(f'BUY CREATE {self.data[0]:2f}, Metaculus: {self.meta[0]},{self.meta[-1]} ')
                self.order = self.buy(data=self.data0)
                
        elif self.meta[-1] > self.meta[0]:
            self.log(f'CLOSE CREATE {self.data[0]:2f}, Metaculus: {self.meta[0]},{self.meta[-1]}')
            self.order = self.close(data=self.data0)
            

    def log (self, txt, dt = None):
        dt = dt or self.datas[0].datetime.date(0)
        buy_count = f'BUY COUNT: {self.buy_counter}'
        sell_count = f'SELL COUNT: {self.sell_counter}'
        print('%s, %s, %s, %s' % (dt.isoformat(), txt,buy_count, sell_count))
    
    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return

        if order.status in [order.Completed]:
            #log if buy
            if order.isbuy():
                self.log(f'BUY EXECUTED, {order.executed.price:.2f}')
                self.buy_counter = self.buy_counter + 1
            #log if sell
            elif order.issell():
                self.log(f'SELL EXECUTED, {order.executed.price:.2f}')
                self.sell_counter = self.sell_counter + 1
            self.bar_executed = len(self)
            
        #Log if order didnt go through
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')
            
        #reset order
        self.order = None

class SPY_Strat(bt.Strategy):
    # Always define parameters first
    def __init__(self):
        self.order = None
        self.vxx = self.data0.close
        self.meta=self.data1.close
        self.spy = self.data2.close
        self.buy_counter = 0
        self.sell_counter = 0


    # Trading logic second
    def next(self):
        if self.order:
            return

        if not self.position:
            if self.meta[-1] < self.meta[0]:
                
                self.log(f'BUY CREATE {self.spy[0]:2f}, Metaculus: {self.meta[0]},{self.meta[-1]} ')
                self.order = self.buy(data=self.data2)
                
        elif self.meta[-1] > self.meta[0]:
            
            self.log(f'CLOSE CREATE {self.spy[0]:2f}, Metaculus: {self.meta[0]},{self.meta[-1]}')
            self.order = self.close(data=self.data2)
            

    def log (self, txt, dt = None):
        dt = dt or self.datas[0].datetime.date(0)
        buy_count = f'BUY COUNT: {self.buy_counter}'
        sell_count = f'SELL COUNT: {self.sell_counter}'
        print('%s, %s, %s, %s' % (dt.isoformat(), txt,buy_count, sell_count))
    
    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return

        if order.status in [order.Completed]:
            #log if buy
            if order.isbuy():
                self.log(f'BUY EXECUTED, {order.executed.price:.2f}')
                self.buy_counter = self.buy_counter + 1
            #log if sell
            elif order.issell():
                self.log(f'SELL EXECUTED, {order.executed.price:.2f}')
                self.sell_counter = self.sell_counter + 1
            self.bar_executed = len(self)
            
        #Log if order didnt go through
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')
            
        #reset order
        self.order = None



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


#Read Data in
vxx_feed = YF_DATA(dataname = vxx_filename, fromdate = start, todate = end)
meta_feed = METACULUS_DATA(dataname = metaculus_filename, fromdate = start, todate = end)
spy_feed = YF_DATA(dataname = spy_filename, fromdate = start, todate = end)


#Add data to cerebro
cerebro.adddata(spy_feed)
#cerebro.adddata(vxx_feed)
cerebro.adddata(meta_feed)




#Add Strat
cerebro.addstrategy(Metaculus_Momentum)

#Add Sharpe Ratio
cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name = 'sharpe_ratio')

#Default position size
#cerebro.addsizer(bt.sizers.SizerFix, stake=1)

#Initial Val
start_portfolio_value = cerebro.broker.getvalue()

run = cerebro.run(stdstats=False)

#cerebro.plot()

#Final Log
end_portfolio_value = cerebro.broker.getvalue()
pnl = end_portfolio_value - start_portfolio_value
sharpe = run[0].analyzers.sharpe_ratio.get_analysis()['sharperatio']
print(f'Starting Portfolio Value: {start_portfolio_value:2f}')
print(f'Final Portfolio Value: {end_portfolio_value:2f}')
print(f'PnL: {pnl:.2f}')
print(f'Sharpe Ratio: {sharpe}')
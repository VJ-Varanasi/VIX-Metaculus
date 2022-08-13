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
        #print(self.order)
        #print(self.position)
        #print(self.datetime.date(ago=0))

        #If there is an order, return
        if self.order:
            return

        #if there is no position
        if not self.position:
            #
            if self.meta[-1] < self.meta[0]:
                self.log(f'BUY CREATE {self.data[0]:2f}, Metaculus: {self.meta[0]},{self.meta[-1]} ')
                self.order = self.buy(data=self.datas[0])
                
        elif self.meta[-1] > self.meta[0]:
            self.log(f'CLOSE CREATE {self.data[0]:2f}, Metaculus: {self.meta[0]},{self.meta[-1]}')
            self.order = self.close(data=self.datas[0])
            

    def log (self, txt, dt = None):
        dt = dt or self.datas[1].datetime.date(0)
        buy_count = f'BUY COUNT: {self.buy_counter}'
        sell_count = f'SELL COUNT: {self.sell_counter}'
        #print('%s, %s, %s, %s' % (dt.isoformat(), txt,buy_count, sell_count))
    
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

class Metaculus_MA(bt.Strategy):
    #moving average parameters
    params = (("pfast", 8), ("pslow", 67), ('lag', 7))
    
    def log (self, txt, dt = None):
        dt = dt or self.datas[0].datetime.date(0)
        #print('%s, %s' % (dt.isoformat(), txt))
    
    def __init__(self):
        self.sma_dataclose = self.data1.close
        self.dataclose = self.datas[0].close
        self.order = None
        
        self.slow_sma = bt.indicators.MovingAverageSimple(self.sma_dataclose, period=self.params.pslow)
        self.fast_sma = bt.indicators.MovingAverageSimple(self.sma_dataclose, period=self.params.pfast)

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
                #USE FOR SPY
                self.log(f'SELL CREATE {self.dataclose[0]:2f}')
                self.order = self.sell(data = self.data0)
                
                #USE FOR VXX
                # self.log(f'BUY CREATE {self.dataclose[0]:2f}')
                # self.order = self.buy(data = self.data0)
            elif self.fast_sma[0] < self.slow_sma[0] and self.fast_sma[-1] > self.slow_sma[-1]:
                #USE FOR SPY
                self.log(f'BUY CREATE {self.dataclose[0]:2f}')
                self.order = self.buy(data = self.data0)
                
                #USE FOR VXX
                # self.log(f'SELL CREATE {self.dataclose[0]:2f}')
                # self.order = self.sell(data = self.data0)
        else:
            #In market so look to Close Trades
            
            #Exit after 5 bars
            if len(self) >= (self.bar_executed + self.params.lag):
                self.log(f'CLOSE CREATE {self.dataclose[0]:2f}')
                self.order = self.close(data = self.data0)

class Metaculus_BOLL(bt.Strategy):

    # Entry Critria:
    #     - Long:
    #         - Price closes below the lower band
    #         - Stop Order entry when price crosses back above the lower band
    #     - Short:
    #         - Price closes above the upper band
    #         - Stop order entry when price crosses back below the upper band
    # Exit Critria
    #     - Long/Short: Price touching the median line

    params = (
        ("period", 20),
        ("devfactor", 2),
        ("size", 20),
        ("debug", False)
        )
    
    def __init__(self):
        self.boll = bt.indicators.BollingerBands(period=self.p.period, devfactor=self.p.devfactor)
    
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
 
        orders = self.broker.get_orders_open()
 
        # Cancel open orders so we can track the median line
        if orders:
            for order in orders:
                self.broker.cancel(order)
 
        if not self.position:
 
            if self.data0.close > self.boll.lines.top:
 
                self.sell(exectype=bt.Order.Stop, price=self.boll.lines.top[0], size=self.p.size)
 
            if self.data.close < self.boll.lines.bot:
                self.buy(exectype=bt.Order.Stop, price=self.boll.lines.bot[0], size=self.p.size)
 
 
        else:
 
 
            if self.position.size > 0:
                self.sell(exectype=bt.Order.Limit, price=self.boll.lines.mid[0], size=self.p.size)
 
            else:
                self.buy(exectype=bt.Order.Limit, price=self.boll.lines.mid[0], size=self.p.size)
    

trading_sec = 'VXX'

#Define Start and End Dates
start = datetime.datetime(2020, 1, 1)
end = datetime.datetime(2022, 4, 1)


#Add Optimization Param
cerebro = bt.Cerebro(optreturn= False)

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


#Add data to cerebro - Add data you are trading first
if trading_sec == "SPY":
    cerebro.adddata(spy_feed)
elif trading_sec == "VXX":
    cerebro.adddata(vxx_feed)

cerebro.adddata(meta_feed)



#Add Strat
cerebro.addstrategy(Metaculus_MA)

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
print(f'Starting Portfolio Value: {start_portfolio_value:2f}')
print(f'Final Portfolio Value: {end_portfolio_value:2f}')
print(f'PnL: {pnl:.2f}')
print(f'Sharpe Ratio: {sharpe}')


# OPTIMIZATION SECTION

# #Add Strat
# cerebro.optstrategy(Metaculus_MA, pfast =range(5,20), pslow = range (50,100), lag = range (5,20))

# #Add Sharpe Ratio
# cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name = 'sharpe_ratio')

#Run Optimixation
#Add Optimization Param

# if __name__ == '__main__':
#     optimized_runs = cerebro.run(stdstats=False)

#     #Pull Results
#     final_results_list = []
#     for run in optimized_runs:
#         for strategy in run:
#             PnL = round(strategy.broker.get_value() - 10000,2)
#             sharpe = strategy.analyzers.sharpe_ratio.get_analysis()
#             final_results_list.append([strategy.params.pfast, strategy.params.pslow, strategy.params.lag, PnL, sharpe['sharperatio']])

#     #Sort Results
#     sort_by_sharpe = sorted(final_results_list, key=lambda x: x[3], reverse=True)

#     #Print Results
#     for line in sort_by_sharpe[:5]:
#         print(line)

#cerebro.plot()


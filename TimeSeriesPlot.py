from time import strftime
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
from math import factorial
from scipy.signal import savgol_filter

#Defining Plot Function
def ts_plot (data_name, start_date, variables, fill):

    partial_name = f'Data/{data_name}_History*'
    filename = glob.glob(partial_name)[0]
    df= pd.read_csv(filename, parse_dates=['DATE'], index_col = ['DATE'])

    df=df.loc[start_date:]
    X= df.index

    for i in variables:
        if fill ==1:
            plt.fill_between(X, y1 = df[i], y2 = -df[i], alpha= 0.5, label = i)
        else:
            plt.plot(X,df[i], label = i)

    plt.title("Timeseries of "+ data_name + " from " + start_date)
    plt.xlabel("Date")
    plt.ylabel(data_name)
    plt.legend()
    plt.show()
    return

#ts_plot(data_name = "VIX", start_date = "2010-01-01", variables = ["CLOSE"], fill =1)
#ts_plot(data_name = "VIX", start_date = "2010-01-01", variables = ["OPEN"], fill =1)
#ts_plot(data_name = "VIX", start_date = "2010-01-01", variables = ["HIGH"], fill =1)
#ts_plot(data_name = "VIX", start_date = "2010-01-01", variables = ["LOW"], fill =1)

#Defining Decomposition Function
def ts_decomp (data_name, start_date, variables, period):
    partial_name = f'Data/{data_name}_History*'
    filename = glob.glob(partial_name)[0]
    df= pd.read_csv(filename, parse_dates=['DATE'], index_col = ['DATE'])

    df=df.loc[start_date:]

    for i in variables:
        result_mul = seasonal_decompose(df[i], model= "multiplicative", extrapolate_trend = 'freq', period = period)
        result_add = seasonal_decompose(df[i], model = 'additive', extrapolate_trend = 'freq' ,period = period)

        plt.rcParams.update({'figure.figsize': (5,5)})
        result_mul.plot().suptitle('Multiplicative Decompose')
        plt.tight_layout()
        result_add.plot().suptitle('Additive Decompose')
        plt.tight_layout()
        plt.show()
    return


#ts_decomp("VIX", start_date = "2010-01-01", variables = ["CLOSE"], period= 252)
#ts_decomp("VIX", start_date = "2010-01-01", variables = ["CLOSE"], period= 30)

#Testing Stationarity

def ADH_test (data_name, start_date, variables):

    partial_name = f'Data/{data_name}_History*'
    filename = glob.glob(partial_name)[0]
    df= pd.read_csv(filename, parse_dates=['DATE'], index_col = ['DATE'])
    df=df.loc[start_date:]

    for i in variables:
        Y = df[i]
        print(i)
        result = adfuller(Y.values, autolag='AIC')
        print(f'ADF Statistic: {result[0]}')
        print(f'p-value: {result[1]}')
        for key, value in result[4].items():
            print('Critial Values:')
            print(f'   {key}, {value}')
    return

#ADH_test("VIX", start_date = "2010-01-01", variables = ["CLOSE"])

def seasonality_test(data_name, start_date, variables):
    partial_name = f'Data/{data_name}_History*'
    filename = glob.glob(partial_name)[0]
    df= pd.read_csv(filename, parse_dates=['DATE'], index_col = ['DATE'])
    df=df.loc[start_date:]

    for i in variables:
        Y = df[i]
        plt.rcParams.update({'figure.figsize':(9,5), 'figure.dpi':120})
        autocorrelation_plot(Y.tolist())
        plt.xlabel("Lag")
        plt.ylabel("Autocorrelation")
        plt.title(data_name + " Autocorrelation Plot")
        plt.show()
    return

#seasonality_test("VIX", start_date = "2010-01-01", variables = ["CLOSE"])

def interpolate_data(data_name, start_date, variables, intervals, method, period, csv):
    partial_name = f'Data/{data_name}_History*'
    filename = glob.glob(partial_name)[0]
    df= pd.read_csv(filename, parse_dates=['DATE'], index_col = ['DATE'])
    df=df.loc[start_date:]
    df= df[variables]
    X = df.index

    if (method == "Linear"):
        resampled_df = df.resample(intervals).asfreq()
        resampled_df = resampled_df.interpolate()
        

    elif(method == "Seasonal"):
        resampled_df = df.resample(intervals).asfreq()
        resampled_df = resampled_df.interpolate()

        print(resampled_df.head())
        sigmas = [0] * len(variables)
        for k in range(len(variables)): 
            yeet = variables[k]
            print(yeet)
            data = resampled_df[yeet]
            print(data.head())
            result_mul = seasonal_decompose(data, model= "multiplicative", extrapolate_trend = 'freq', period = period)
            sigmas[k] = np.std(result_mul.seasonal)

        for i in resampled_df.index:
            if (i not in X):
                for j in variables:
                    sigma = sigmas[variables.index(j)]
                    resampled_df.at[i, j]= resampled_df.at[i, j] + np.random.normal(0, sigma) 
    if (csv == 1):
        filename = "Data/{}_{}_interpolation_{}.csv".format(data_name,method,intervals)
        resampled_df.to_csv(filename)

    for m in variables:
        plt.plot(resampled_df.index,resampled_df[m], label = m)
        plt.title( method + " Timeseries of "+ data_name + " from " + start_date + " with " + intervals)
        plt.xlabel("Date")
        plt.ylabel(data_name)
        plt.legend()
        plt.show()
    
    return(resampled_df)

#interpolate_data("VIX", "2010-01-01", ["CLOSE"], '1H', "Seasonal", 30, 1)

#interpolate_data("VIX", "2010-01-01", ["CLOSE"], '1H', "Linear", 30, 1)


def vix_user_plot(data_name,start_date, remove_dates, smooth):
    
    activity = pd.read_csv("Data/visitors-actives.csv")
    partial_name = f'Data/{data_name}_History*'
    filename = glob.glob(partial_name)[0]
    print(filename)
    vix_data= pd.read_csv(filename, parse_dates=['DATE'], index_col = ['DATE'])
    vix_data = vix_data.loc[start_date:]
    vix_data.index = vix_data.index.strftime('%m/%d/%Y')

   
    activity["Day Index"]= pd.to_datetime(activity["Day Index"]).dt.strftime('%m/%d/%Y')
    activity = activity.rename(columns = {"Day Index" : "DATE", "1 Day Active Users": "Users"})
    vix_data = vix_data.drop(columns = ["OPEN", "HIGH", "LOW"])

    activity = activity.replace(',','',regex=True)
    activity["Users"] = pd.to_numeric(activity["Users"])

    for i in remove_dates:
        activity['DATE']
        index_val = activity.index[activity["DATE"]==i][0]
        activity.loc[index_val,"Users"] = (int(activity.at[index_val + 1,"Users"]) + int(activity.at[index_val - 1,"Users"]))/2
    
    df = vix_data.merge(activity, how= 'inner', on = 'DATE')

    df=df.set_index("DATE")

    
    fig, ax1 = plt.subplots()

    color = 'tab:blue'
    ax1.set_xlabel('Date')
    ax1.set_ylabel(data_name, color=color)
    ax1.plot(df.index, df["CLOSE"], color=color)

    ax1.xaxis.set_major_locator(mdates.MonthLocator())

    ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis

      # we already handled the x-label with ax1
    
    color = 'tab:orange'
    if smooth[1] != 0:
        ax2.plot(df.index, savgol_filter(df["Users"], smooth[0], smooth[1]), color=color)
        ax2.set_ylabel('Smoothened User Activity', color=color)
    else:
        ax2.plot(df.index, df["Users"], color=color)
        ax2.set_ylabel('User Activity', color=color)

    ax2.tick_params(axis='y', labelcolor=color)

    fig.tight_layout()  # otherwise the right y-label is slightly clipped
    plt.title("{} Index and Metaculus User Activity".format(data_name))
    plt.show()
    return

vix_user_plot("VXX", "2022-01-01",["03/08/2022", "01/04/2022", "01/05/2022"], [0, 0])
vix_user_plot("VXX", "2022-01-01",["03/08/2022", "01/04/2022", "01/05/2022"], [15, 4])
vix_user_plot("VXX", "2022-01-01",["03/08/2022", "01/04/2022", "01/05/2022"], [30, 4])
vix_user_plot("VXX", "2022-01-01",["03/08/2022", "01/04/2022", "01/05/2022"], [15, 6])
vix_user_plot("VXX", "2022-01-01",["03/08/2022", "01/04/2022", "01/05/2022"], [30, 6])
#vix_user_plot("VIX", "2022-01-01",["03/08/2022", "01/04/2022", "01/05/2022"], [0, 0])
#vix_user_plot("VIX", "2022-01-01",["03/08/2022", "01/04/2022", "01/05/2022"], [15, 4])
#vix_user_plot("VIX", "2022-01-01",["03/08/2022", "01/04/2022","01/05/2022"], [30, 4])
#vix_user_plot("VIX", "2022-01-01",["03/08/2022", "01/04/2022","01/05/2022"], [45, 4])
#vix_user_plot("VIX", "2022-01-01",["03/08/2022", "01/04/2022","01/05/2022"], [15, 6])
#vix_user_plot("VIX", "2022-01-01",["03/08/2022", "01/04/2022","01/05/2022"], [30, 6])
#vix_user_plot("VIX", "2022-01-01",["03/08/2022", "01/04/2022","01/05/2022"], [45, 6])

def old_vix_user_plot(data_name, start_date, remove_spike, smooth, percent_cutoff, percent_change):
    remove_date =["03/08/2022", "01/04/2022"]
    
    activity = pd.read_csv("Data/visitors-actives.csv")
    partial_name = f'Data/{data_name}_History*'
    filename = glob.glob(partial_name)[0]
    vix_data= pd.read_csv(filename, parse_dates=['DATE'], index_col = ['DATE'])
    vix_data = vix_data.loc[start_date:]
    vix_data.index = vix_data.index.strftime('%m/%d/%Y')

   
    activity["Day Index"]= pd.to_datetime(activity["Day Index"]).dt.strftime('%m/%d/%Y')
    activity = activity.rename(columns = {"Day Index" : "DATE", "1 Day Active Users": "Users"})
    vix_data = vix_data.drop(columns = ["OPEN", "HIGH", "LOW"])

    activity = activity.replace(',','',regex=True)
    activity["Users"] = pd.to_numeric(activity["Users"])

    if(remove_spike == 1):
        for i in remove_date:
            activity['DATE']
            index_val = activity.index[activity["DATE"]==i][0]
            activity.loc[index_val,"Users"] = (int(activity.at[index_val + 1,"Users"]) + int(activity.at[index_val - 1,"Users"]))/2
    
    if(smooth == 1):
        n = len(activity["Users"])
        new_col = [0] * n
        for i in range(n):
            if(i < 7):
                new_col[i] = activity.at[i,"Users"]
            else:
                if (abs(activity.at[i,"Users"] - activity.at[i-7,"Users"] ) < (activity.at[i-7,"Users"]*percent_cutoff)):
                    new_col[i] = new_col[i-1]
                else:
                    new_col[i] = activity.at[i,"Users"] 

        activity["Smooth_Users"] = new_col 

    if(percent_change ==1):
        n = len(activity["Users"])
        new_col = [0] * n
        scale = 1
        for i in range(n):
            if(i < scale):
                new_col[i] = activity.at[i,"Users"]
            else:
                new_col[i] = abs(activity.at[i,"Users"] - activity.at[i-scale,"Users"] )/activity.at[i-scale,"Users"]
        activity["Percent_Change"] = new_col 

    df = vix_data.merge(activity, how= 'inner', on = 'DATE')

    df=df.set_index("DATE")

    fig, ax1 = plt.subplots()

    color = 'tab:blue'
    ax1.set_xlabel('Date')
    ax1.set_ylabel('VIX Index', color=color)
    ax1.plot(df.index, df["CLOSE"], color=color)

    ax1.xaxis.set_major_locator(mdates.MonthLocator())

    ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis

      # we already handled the x-label with ax1
    if (smooth ==1):
        color = 'tab:red'
        ax2.plot(df.index,df["Smooth_Users"], color=color)
        ax2.set_ylabel('Smooth User Activity', color=color)
    elif (percent_change ==1):
        color = 'tab:green'
        ax2.plot(df.index,df["Percent_Change"], color=color)
        ax2.set_ylabel('Percent Change in User Activity', color=color)
    else:
        color = 'tab:orange'
        ax2.plot(df.index,df["Users"], color=color)
        ax2.set_ylabel('User Activity', color=color)

    ax2.tick_params(axis='y', labelcolor=color)

    fig.tight_layout()  # otherwise the right y-label is slightly clipped
    if(smooth == 1):
        plt.title("VIX Index and Metaculus User Activity with {}% Filter".format(percent_cutoff*100))
    elif(percent_change == 1):
        plt.title("VIX Index and Metaculus Percent Change in User Activity")
    else:
        plt.title("VIX Index and Metaculus User Activity")
    plt.show()
    return
    
#old_vix_user_plot("VIX", "2022-01-01", 1, 0, 0.10, 0)
#old_vix_user_plot("VIX", "2022-01-01", 1, 1, 0.30, 0)
#old_vix_user_plot("VIX", "2022-01-01", 1, 1, 0.50, 0)

def vix_shifted_user_plot(data_name, start_date, scale, time_delta):
    remove_date ="03/08/2022"
    
    activity = pd.read_csv("Data/visitors-actives.csv")
    partial_name = f'Data/{data_name}_History*'
    filename = glob.glob(partial_name)[0]
    vix_data= pd.read_csv(filename, parse_dates=['DATE'], index_col = ['DATE'])
    vix_data = vix_data.loc[start_date:]
    vix_data.index = vix_data.index.strftime('%m/%d/%Y')

   
    activity["Day Index"]= pd.to_datetime(activity["Day Index"]).dt.strftime('%m/%d/%Y')
    activity = activity.rename(columns = {"Day Index" : "DATE", "1 Day Active Users": "Users"})
    vix_data = vix_data.drop(columns = ["OPEN", "HIGH", "LOW"])

    activity = activity.replace(',','',regex=True)
    activity["Users"] = pd.to_numeric(activity["Users"])

    
    activity['DATE']
    index_val = activity.index[activity["DATE"]==remove_date][0]
    activity.loc[index_val,"Users"] = (int(activity.at[index_val + 1,"Users"]) + int(activity.at[index_val - 1,"Users"]))/2
   
    df = vix_data.merge(activity, how= 'inner', on = 'DATE')

    df["DATE"] =pd.to_datetime(df["DATE"])

    n = len(df["DATE"])
    new_col = [0] * n
    for i in range(n):
        if(i < scale):
                    new_col[i] = df.at[i,"DATE"].strftime('%m/%d/%Y')
        else:
            percent_diff = (df.at[i,"Users"] - df.at[i-scale,"Users"]) /df.at[i-scale,"Users"]
            if(percent_diff <= 0):
                gamma = 0
            else:
                gamma = time_delta * percent_diff
            new_col[i] = (df.at[i,"DATE"] +datetime.timedelta(gamma)) .strftime('%m/%d/%Y')
    df["New_Date"] = new_col 


    fig, ax1 = plt.subplots()

    color = 'tab:blue'
    ax1.set_xlabel('Date')
    ax1.set_ylabel('VIX Index', color=color)
    ax1.plot(df.index, df["CLOSE"], color=color)

    ax1.xaxis.set_major_locator(mdates.MonthLocator())

    ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis

      # we already handled the x-label with ax1
    color = 'tab:green'
    ax2.plot(df["New_Date"],df["Users"], color=color)
    ax2.set_ylabel('Shifted User Activity', color=color)
    ax2.tick_params(axis='y', labelcolor=color)

    fig.tight_layout()  # otherwise the right y-label is slightly clipped
    plt.title("VIX Index vs Metaculus User Activity with {} time shift".format(time_delta))
    plt.show()
    return

#vix_shifted_user_plot("VIX", "2022-01-01",1, 30)
#vix_shifted_user_plot("VIX", "2022-01-01",7, 10)
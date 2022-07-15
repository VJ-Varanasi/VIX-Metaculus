import requests
import time
import datetime
import os
import pandas as pd


def updateData (url, data_name):

    filename = os.path.join('Data',data_name + "_" + str(datetime.date.today()) + ".csv")
    if not (os.path.exists(filename)):
        #Downloads Data from URL
        req= requests.get(url)
        
        #Saves data as CSV
        with open(filename, "wb") as f:
            for chunk in req.iter_content(chunk_size =8192):
                if chunk:
                    f.write(chunk)
        
        #Deletes old file if it exists
        old_name= "Data/" + data_name + "_" + str(datetime.date.today() - datetime.timedelta(days = 1)) + ".csv"
        if (os.path.exists(old_name)):
            os.remove(old_name)
    return 

def get_querydate ():
    #Get the day of the week
    day_of_week = datetime.date.today().weekday()
    
    #If Monday or Sunday get Friday
    if (day_of_week == 0):
        date_of_query = datetime.date.today() - datetime.timedelta(days = 3)
    elif(day_of_week == 6):
        date_of_query = datetime.date.today() - datetime.timedelta(days = 2)
    
    #Otherwise, just get day before
    else:
       date_of_query = datetime.date.today() - datetime.timedelta(days = 1)

    number = int(time.mktime(datetime.datetime(date_of_query.year, date_of_query.month, date_of_query.day,19,00).timetuple()))
    return(number)

def get_yf (url, data_name):
    filename = os.path.join('Data',data_name + "_" + str(datetime.date.today()) + ".csv")
    #Check if File Exists
    if not (os.path.exists(filename)):
        #Save data as dataframe
        df=pd.read_csv(url)
        print(df.columns)
        df.columns = df.columns.str.upper()
        print(df.columns)
            #Save data as CSV
        df.to_csv(filename)

            #Remove Old data if applicable
        old_name= "Data/" + data_name + "_" + str(datetime.date.today() - datetime.timedelta(days = 1)) + ".csv"
        if (os.path.exists(old_name)):
            os.remove(old_name)
    return

query_date = get_querydate() 
vxx_url = f'https://query1.finance.yahoo.com/v7/finance/download/VXX?period1=1516924800&period2={query_date}&interval=1d&events=history&includeAdjustedClose=true'

get_yf(vxx_url, "VXX_History")


updateData("https://cdn.cboe.com/api/global/us_indices/daily_prices/VVIX_History.csv","VVIX_History")
updateData("https://cdn.cboe.com/api/global/us_indices/daily_prices/VIX_History.csv","VIX_History")
updateData("https://cdn.cboe.com/api/global/us_indices/daily_prices/VIX9D_History.csv", "VIX9D_History")
updateData("https://www.cboe.com/us/futures/market_statistics/historical_data/cfevoloi.csv", "VIX_Futures_Interest")


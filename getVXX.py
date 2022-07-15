# import requests
# from bs4 import BeautifulSoup

# headers = {'User-Agent' :'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.109 Safari/537.36'}
# url = "https://finance.yahoo.com/quote/VXX"

# r = requests.get(url)

# soup = BeautifulSoup(r.text, 'html.parser')

# print(soup.title.text)

# price = soup.find('fin-streamer', {'class': "Fw(b) Fz(36px) Mb(-4px) D(ib)"}).text
# change = soup.find('fin-streamer', {'class':"Fw(500) Pstart(8px) Fz(24px)"}).text
# print(price)
# print(change)

#MESSY CODE USED AS SCRAP WORK

import time
import datetime
import requests
import pandas as pd

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

query_date = get_querydate() 

print(query_date)

print(time.localtime(query_date))


my_url = f'https://query1.finance.yahoo.com/v7/finance/download/VXX?period1=1516924800&period2={query_date}&interval=1d&events=history&includeAdjustedClose=true'

print(my_url)

# url = requests.get("https://query1.finance.yahoo.com/v7/finance/download/VXX?period1=1516924800&period2=1646352000&interval=1d&events=history&includeAdjustedClose=true")
# req= requests.get(url)
# with open("trial", "wb") as f:
#             for chunk in req.iter_content(chunk_size =8192):
#                   if chunk:
#                       f.write(chunk)

df = pd.read_csv(my_url)

#updateData("https://query1.finance.yahoo.com/v7/finance/download/VXX?period1=1516924800&period2=1646265600&interval=1d&events=history&includeAdjustedClose=true", "trial 2")
#https://query1.finance.yahoo.com/v7/finance/download/VXX?period1=1516924800&period2=1645833600&interval=1d&events=history&includeAdjustedClose=true

# def updateData (url, data_name):
#      filename = os.path.join('Data',data_name + "_" + str(date.today()) + ".csv")
#      if not (os.path.exists(filename)):
#         #Downloads Data from URL
#          req= requests.get(url)
        
        
#          #Saves data as CSV
#          with open(filename, "wb") as f:
#              for chunk in req.iter_content(chunk_size =8192):
#                  if chunk:
#                      f.write(chunk)
        
#          #Deletes old file if it exists
#          old_name= "Data/" + data_name + "_" + str(date.today() - timedelta(days = 1)) + ".csv"
#          if (os.path.exists(old_name)):
#              os.remove(old_name)
#          return
#      return 


# today= datetime.date.today()

# print(time.mktime(datetime.datetime(datetime.date.today().year, datetime.date.today().month,datetime.date.today().day -1,19,00).timetuple()))
# print(time.mktime(datetime.datetime(datetime.date.today().year, datetime.date.today().month,datetime.date.today().day -2,19,00).timetuple()))
# print(time.mktime(datetime.datetime(2022, 2, 25,19,00).timetuple()))
# print(time.mktime(datetime.datetime(2022, 2, 26,19,00).timetuple()))
# print(time.mktime(datetime.datetime(2022, 2, 27,19,00).timetuple()))
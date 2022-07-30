import pandas as pd
import os

#Smoothening Function
def smooth(activity, remove_date, smooth_len):
    activity["Users"] = pd.to_numeric(activity["Users"])
    index_val = activity.index[activity["Date"]==remove_date][0]
    
    avg_user =  (sum(activity["Users"].iloc[int(index_val-smooth_len/2):int(index_val+ 1+smooth_len/2)]) - int(activity.at[index_val,"Users"]))/smooth_len
    
    #activity.loc[index_val,"Users"] = (int(activity.at[index_val + 2,"Users"]) + int(activity.at[index_val + 1,"Users"]) + int(activity.at[index_val - 1,"Users"])+ int(activity.at[index_val - 2,"Users"]))/smooth_len
    activity.loc[index_val,"Users"] = int(avg_user)
    return(activity)

#Metaculus Raw data
metaculus_filename = 'Data/visitors-actives.csv'

#Reading in CSV
data = pd.read_csv(metaculus_filename)

#Converting to datetime index
data['Day Index'] = pd.to_datetime(data['Day Index'], format = '%m/%d/%y')

#Finding last date
last_day = data['Day Index'].iloc[-1]

#Renaming Columns
data = data.rename(columns={"Day Index": "Date", "1 Day Active Users": "Users"})

#Remove all commas
data = data.replace(',','', regex=True)

#Saving modified csv
filename = os.path.join('Data', 'Metaculus_Users_' + str(last_day)[0:10] + ".csv")
data.to_csv(filename, index=False)

#Optional Smoothing
smooth_dates = ["03/08/2022", "01/04/2022"]

#Controls how many days to average over
smooth_len = 2

for i in smooth_dates:
    smooth_data = smooth(data, i,smooth_len)

smooth_filename = os.path.join('Data', str(smooth_len) + '_Day_Smooth_Metaculus_Users_' + str(last_day)[0:10] + ".csv")
smooth_data.to_csv(smooth_filename, index=False)
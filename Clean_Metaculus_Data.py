import pandas as pd
import os

#Metaculus Raw data
metaculus_filename = 'Data/visitors-actives.csv'

#Reading in CSV
data = pd.read_csv(metaculus_filename)

#Converting to datetime index
data['Day Index'] = pd.to_datetime(data['Day Index'], format = '%m/%d/%y')

#Finding last date
last_day = data['Day Index'].iloc[-1]

#Saving modified csv
filename = os.path.join('Data', 'Metaculus_Users_' + str(last_day)[0:10] + ".csv")
data.to_csv(filename)

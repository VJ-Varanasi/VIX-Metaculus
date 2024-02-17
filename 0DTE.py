from yahooquery import Ticker
import datetime
import pandas as pd


stocklist =['^SPX']
t = Ticker(stocklist, asynchronous=True)
df = t.option_chain

td= datetime.date.today().strftime('%Y-%m-%d')


df = df[df.index.isin([td], level = "expiration")]
df.reset_index(inplace=True)
df=df.drop(["contractSymbol", "currency", "contractSize"], axis = 1)
df["Midpiont"] = (df["ask"] + df["bid"])/2



csv_file_path = 'Data/0DTE.csv'

# Try to read the existing CSV file (if it exists)
try:
    existing_df = pd.read_csv(csv_file_path)
    # If the file exists, append the new data to it
    updated_df = existing_df.append(df, ignore_index=True)
except FileNotFoundError:
    # If the file doesn't exist, create a new DataFrame with the current data
    updated_df = df

# Write the updated DataFrame to the CSV file
updated_df.to_csv(csv_file_path, index=False)
#Integrating milli-Second Spot Data (/1000 - to less the burden) and classyifying them in Candle components

import requests
import pandas as pd
import numpy as np
import pytz
from datetime import datetime

class vix_india:
    def __init__(self, starting_date, ending_date=None):
        self.starting_date = starting_date
        if ending_date is None:
            ending_date = datetime.now().strftime("%d-%m-%Y")# to getting the latest closing iv
        self.ending_date = ending_date
        self.url = f"https://www.nseindia.com/api/historical/vixhistory?from={starting_date}&to={ending_date}"
        self._session = requests.Session()
        self._session.headers = {
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        }
        self._session.get("https://www.nseindia.com/reports-indices-historical-vix")

    def fetch_vix_data(self):
        try:
            response = self._session.get(self.url, timeout=10)
            response.raise_for_status()  # Raise an exception for 4xx and 5xx status codes
            data_vix = response.json()
            vix_data = pd.json_normalize(data_vix["data"])
            return vix_data
        except requests.RequestException as ex:

            return pd.DataFrame()

# Verification
if __name__ == "__main__":
    vix_india_ohcs = vix_india(starting_date="17-04-2024")
    data_vix = vix_india_ohcs.fetch_vix_data()

dataframe_vix = pd.DataFrame(data_vix)
vix = dataframe_vix.iloc[-1, -1]
Nifty_Vix = dataframe_vix.iloc[-1, 7]


class SpotPrice:
    def __init__(self, identifier="NIFTY 50", name="NIFTY 50", timeout=5):
        self.url = "https://www.nseindia.com/api/chart-databyindex?index=NIFTY%2050&indices=true"
        self._session = requests.Session()
        self._session.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.0.0 Safari/537.36",
            "Accept": "*/*",
            "Accept-Language": "en-US,en;q=0.5"
        }
        self._timeout = timeout
        self._session.get("https://www.nseindia.com/", timeout=5)

    def fetch_data(self):
        try:
            response = self._session.get(url=self.url, timeout=5)  # Increased timeout
            data = response.json()
            graph_data = data.get("grapthData", [])

            timestamps = [entry[0] / 1000 for entry in graph_data]  # Convert milliseconds to seconds
            date_timings = pd.to_datetime(timestamps, unit='s')  # Convert timestamps to datetime objects

            values = [entry[1] for entry in graph_data]
            df = pd.DataFrame({"Timestamp": date_timings, "Value": values})
            return df

        except Exception as ex:
            print("Error: {}".format(ex))
            self._session.get("https://www.nseindia.com/", timeout=self._timeout)  # to renew the session
            return pd.DataFrame()

    def create_candles(self, spot_data, interval_minutes=15):
        try:
            # Set 'Timestamp' as the index
            spot_data.set_index('Timestamp', inplace=True)

            # Resample data to create candles
            candles = spot_data.resample(f'{interval_minutes}min').agg({
                'Value': 'ohlc'
            })
            candles.columns = ['Open', 'High', 'Low', 'Close']
            candles.dropna(inplace=True)

            # Reset index to make 'Timestamp' a column again
            candles.reset_index(inplace=True)

            return candles

        except Exception as ex:
            print("Error creating candles: {}".format(ex))
            return pd.DataFrame()

# Testing the data
if __name__ == "__main__":
    obj = SpotPrice(identifier="NIFTY 50")
    spot_mtd = obj.fetch_data()
    candles = obj.create_candles(spot_mtd, interval_minutes=15)
    candles['Time'] = candles['Timestamp'].dt.time  # Extract time component
    candles['Date'] = candles['Timestamp'].dt.date  # Extract date component
 #   print("Classified Candle Components:-")
 #   print(candles.head())





#Importing Plotly and making candles




market_open = candles[candles['Time'].astype(str) == "09:15:00"]['Open'].iloc[0]
resistance = candles[candles['Time'].astype(str) == "09:15:00"]['High'].iloc[0]
support = candles[candles['Time'].astype(str) == "09:15:00"]['Low'].iloc[0]
current_spot = spot_mtd.iloc[-1, -1]
it_money = (market_open // 50) * 50
print(f'Current spot price: {current_spot}; '
      f'Market open: {market_open}; '
      f'Resistance bar: {resistance}; '
      f'Support bar: {support}; '
      f'Strike price for trade: {it_money}; '
      f'Nifty Vix data: {Nifty_Vix}')


import pandas as pd

def Buy():
    buy_calls_data = []  # List to store buy call data
    buy_puts_data = []  # List to store buy put data
    prev_row = None  # Variable to store previous row data
    prev1_row = None 

    if Nifty_Vix>15:
        for index, row in candles.iterrows():
            if prev_row is not None and (prev_row['Open'] <= resistance):
                if row['Close'] > resistance:
                    buy_calls_data.append([row['Time'], it_money, support])
            prev_row = row  # Update previous row data

        for index, row in candles.iterrows():
            if prev1_row is not None and (prev1_row['Open'] >= support):
                if row['Close'] < support:
                    buy_puts_data.append([row['Time'], it_money, resistance])
            prev1_row = row  # Update previous row data

        buy_calls_df = pd.DataFrame(buy_calls_data, columns=['Time', 'Strike Price', 'Stoploss'])
        buy_puts_df = pd.DataFrame(buy_puts_data, columns=['Time', 'Strike Price', 'Stoploss'])

        return print(buy_calls_df), print(buy_puts_df)
    
    else:
        print("Market is Range Bound. Do not execute trades.")

Buy()

# Example usage:
# Assuming candles, resistance, support, and it_money are defined
#buy_calls_df, buy_puts_df = Buy(Nifty_Vix, candles, resistance, support, it_money)
#print(buy_calls_df)
#print(buy_puts_df)








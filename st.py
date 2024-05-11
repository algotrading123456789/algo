import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import requests

st.title('Welcome to Option Maniancs')

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
            st.error(f"Error: {ex}")
            self._session.get("https://www.nseindia.com/", timeout=self._timeout)  # to renew the session
            return pd.DataFrame()

# Fetching data
obj = SpotPrice(identifier="NIFTY 50")
spot_mtd = obj.fetch_data()

# Create Candlestick chart
trace = go.Candlestick(x=spot_mtd["Timestamp"],
                    open=spot_mtd['Open'],
                    high=spot_mtd['High'],
                    low=spot_mtd['Low'],
                    close=spot_mtd['Close'])

# Create figure
fig = go.Figure(data=[trace])

# Add layout
fig.update_layout(title='NIFTY 50 Candlestick Chart',
                xaxis_title='Time',
                yaxis_title='Price',
                yaxis=dict(tickformat=",d"),  # Use comma as thousands separator and display full number
                xaxis=dict(
                    tickvals=list(range(len(spot_mtd))),
                    ticktext=spot_mtd['Timestamp'].apply(lambda x: x.strftime('%H:%M:%S'))
                ))

# Display the plot
st.plotly_chart(fig)

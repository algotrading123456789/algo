import streamlit as st
import requests
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime

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
            print("Error: {}".format(ex))
            self._session.get("https://www.nseindia.com/", timeout=self._timeout)  # to renew the session
            return pd.DataFrame()

# Testing the data
if __name__ == "__main__":
    obj = SpotPrice(identifier="NIFTY 50")
    spot_mtd = obj.fetch_data()
    
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
import plotly.graph_objects as go
# Extract day from the 'Time' column
day = candles.loc[0, 'Date'].strftime('%d-%m-%Y')

# Create candlestick trace
trace = go.Candlestick(x=candles.index,
                    open=candles['Open'],
                    high=candles['High'],
                    low=candles['Low'],
                    close=candles['Close'])
                        

# Create figure and add trace
fig = go.Figure(data=[trace])


# Add sliders for plot width and height
width = st.sidebar.slider("Plot width", 1, 25, 15)  # Default value set to 15
height = st.sidebar.slider("Plot height", 1, 25, 10)  # Default value set to 10

# Update layout with the day in the title
fig.update_layout(title=f'NIFTY 50 Candlestick Chart - {day}',
                xaxis_title='Time',
                yaxis_title='Price',
                yaxis=dict(tickformat=",d"),  # Use comma as thousands separator and display full number
                xaxis=dict(
                    tickvals=list(range(len(candles))),
                    ticktext=candles['Time'].apply(lambda x: x.strftime('%H:%M:%S'))
                ))

# Add horizontal lines for support and resistance
fig.add_shape(type="line",
            x0=candles.index[1], y0=candles['High'][1],
            x1=candles.index[-1], y1=candles['High'][1],
            line=dict(color="Purple", width=2, dash="dash"),
            name="Resistance")
fig.add_shape(type="line",
            x0=candles.index[1], y0=candles['Low'][1],
            x1=candles.index[-1], y1=candles['Low'][1],
            line=dict(color="Black", width=2, dash="dash"),
            name="Support")


# Add annotations for labels
fig.update_layout(annotations=[
    dict(
        x=candles.index[-1],
        y=candles['High'][1],
        xref="x",
        yref="y",
        text="Resistance",
        showarrow=True,
        font=dict(
            color="Purple",
            size=12
        ),
        ax=-30,
        ay=-20
    ),
    dict(
        x=candles.index[-1],
        y=candles['Low'][1],
        xref="x",
        yref="y",
        text="Support",
        showarrow=True,
        font=dict(
            color="Black",
            size=12
        ),
        ax=-30,
        ay=20
    )
])


# Display the plot
st.plotly_chart(fig)


# st.plotly_chart(fig)

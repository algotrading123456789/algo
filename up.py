import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go  # Import Plotly
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

# Importing Plotly and making candles
import plotly.graph_objects as go

# Assuming `candles` dataframe is available

# Extract day from the 'Time' column
day = spot_mtd.loc[0, 'Timestamp'].strftime('%d-%m-%Y')

# Create candlestick trace
trace = go.Candlestick(x=spot_mtd['Timestamp'],
                       open=spot_mtd['Open'],
                       high=spot_mtd['High'],
                       low=spot_mtd['Low'],
                       close=spot_mtd['Close'])

# Create figure and add trace
fig = go.Figure(data=[trace])

# Update layout with the day in the title
fig.update_layout(title=f'NIFTY 50 Candlestick Chart - {day}',
                  xaxis_title='Time',
                  yaxis_title='Price',
                  yaxis=dict(tickformat=",d"),  # Use comma as thousands separator and display full number
                  xaxis=dict(tickvals=list(range(len(spot_mtd))),
                             ticktext=spot_mtd['Timestamp'].apply(lambda x: x.strftime('%H:%M:%S')))
                  )

# Add horizontal lines for support and resistance
# Assuming `candles` dataframe is available
fig.add_shape(type="line",
              x0=spot_mtd.index[1], y0=spot_mtd['High'][1],
              x1=spot_mtd.index[-1], y1=spot_mtd['High'][1],
              line=dict(color="Purple", width=2, dash="dash"),
              name="Resistance")
fig.add_shape(type="line",
              x0=spot_mtd.index[1], y0=spot_mtd['Low'][1],
              x1=spot_mtd.index[-1], y1=spot_mtd['Low'][1],
              line=dict(color="Black", width=2, dash="dash"),
              name="Support")

# Add annotations for labels
fig.update_layout(annotations=[
    dict(
        x=spot_mtd.index[-1],
        y=spot_mtd['High'][1],
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
        x=spot_mtd.index[-1],
        y=spot_mtd['Low'][1],
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

# Display the plot using st.plotly_chart()
st.plotly_chart(fig)

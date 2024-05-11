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
    
    if not spot_mtd.empty:
        # Extract day from the 'Time' column
        day = spot_mtd.loc[0, 'Timestamp'].strftime('%d-%m-%Y')

        # Create line plot
        fig = go.Figure()

        fig.add_trace(go.Scatter(x=spot_mtd['Timestamp'], y=spot_mtd['Value'], mode='lines', name='Spot Price'))

        # Update layout with the day in the title
        fig.update_layout(title=f'NIFTY 50 Spot Price Chart - {day}',
                          xaxis_title='Time',
                          yaxis_title='Price',
                          yaxis=dict(tickformat=",d"))  # Use comma as thousands separator and display full number

        st.plotly_chart(fig)
    else:
        st.write("No data available to display.")

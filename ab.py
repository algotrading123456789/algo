import streamlit as st
import schedule
import time
import requests
import pandas as pd
import numpy as np
import pytz
from datetime import datetime


# Inject custom CSS to expand the layout
st.markdown(
    """
    <style>
    .full-width {
        width: 100%;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Use the full-width class for your content
st.markdown('<div class="full-width">Your content here</div>', unsafe_allow_html=True)


st.title('Navigate Your Trades')


def job():
    #Integrating milli-Second Spot Data (/1000 - to less the burden) and classyifying them in Candle components

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
    Nifty_Vix = dataframe_vix.iloc[-1, 7]
    Nifty_Vix_Y = dataframe_vix.iloc[-2, 7]
    D_Vix = Nifty_Vix - Nifty_Vix_Y
    Diff_Vix = "{:.2f}%".format(D_Vix)


    class SpotPrice:
        def __init__(self, identifier="NIFTY 50", name="NIFTY 50", timeout=15):
            self.url = "https://www.nseindia.com/api/chart-databyindex?index=NIFTY%2050&indices=true"
            self._session = requests.Session()
            self._session.headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.0.0 Safari/537.36",
                "Accept": "*/*",
                "Accept-Language": "en-US,en;q=0.5"
            }
            self._timeout = timeout
            self._session.get("https://www.nseindia.com/", timeout=15)

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

    st.plotly_chart(fig)



    market_open = candles[candles['Time'].astype(str) == "09:15:00"]['Open'].iloc[0]
    resistance = candles[candles['Time'].astype(str) == "09:15:00"]['High'].iloc[0]
    support = candles[candles['Time'].astype(str) == "09:15:00"]['Low'].iloc[0]
    current_spot = spot_mtd.iloc[-1, -1]
    formatted_spot = "{:,}".format(current_spot)
    dif_spot = current_spot - market_open
    d_spot = (dif_spot)*100/market_open
    delta_spot = "{:.2f}%".format(d_spot)
    it_money = (market_open // 50) * 50


    st.metric("Spot price", formatted_spot, delta_spot)
    st.metric('Market Open at', market_open)
    st.metric('Volatility', Nifty_Vix, Diff_Vix)
    st.write(f'Optimal Strike price for trade: {it_money}')
    st.write(f'Resistance bar: {resistance}')
    st.write(f'Support bar: {support}')



    def Buy():
        buy_calls_data = []  # List to store buy call data
        buy_puts_data = []  # List to store buy put data
        prev_row = None  # Variable to store previous row data
        prev1_row = None 

        if Nifty_Vix > 15:
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

            return buy_calls_df, buy_puts_df, None  # Return DataFrames and None for else case
        else:
            return None, None, "Disclaimer: Market lacks volatility. Investment in Options is not advisable. Refrain from executing trades."

    buy_calls_df, buy_puts_df, message = Buy()


    if buy_calls_df is not None:
        if not buy_calls_df.empty:
            st.write("**Call Trades to be executed**")
            st.dataframe(buy_calls_df)
        else:
            st.write("**Refrain from buying Call Options**")
            st.dataframe(buy_calls_df)
    else:
        st.write("**Refrain from buying Call Options**")
        st.dataframe(buy_calls_df)


    if buy_puts_df is not None:
        if not buy_puts_df.empty:
            st.write("**Put Trades to be executed**")
            st.dataframe(buy_puts_df)
        else:
            st.write("**Refrain from buying Put Options**")
            st.dataframe(buy_puts_df)
    else:
        st.write("**Refrain from buying Put Options**")
        st.dataframe(buy_puts_df)


    if message:
        st.title(f"{message}")

job()

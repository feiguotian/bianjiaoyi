import streamlit as st
import pandas as pd
import requests
import os
import zipfile
import csv
from io import StringIO
from datetime import datetime
import matplotlib.pyplot as plt

# Function to download Binance Kline data
def download_binance_data(symbol, interval, start_date, end_date):
    base_url = f"https://api.binance.com/api/v3/klines"
    params = {
        "symbol": symbol,
        "interval": interval,
        "startTime": int(datetime.strptime(start_date, "%Y-%m-%d").timestamp() * 1000),
        "endTime": int(datetime.strptime(end_date, "%Y-%m-%d").timestamp() * 1000),
        "limit": 1000  # max limit, can adjust based on the needs
    }
    response = requests.get(base_url, params=params)
    
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        st.error(f"Error: {response.status_code}")
        return None

# Function to process and save Kline data
def process_kline_data(kline_data):
    # Columns: Open time, Open, High, Low, Close, Volume, Close time, Quote asset volume, Number of trades, Taker buy base asset volume, Taker buy quote asset volume, Ignore
    processed_data = []
    
    for kline in kline_data:
        processed_data.append({
            "timestamp": datetime.utcfromtimestamp(kline[0] / 1000),
            "open": float(kline[1]),
            "high": float(kline[2]),
            "low": float(kline[3]),
            "close": float(kline[4]),
            "volume": float(kline[5]),
        })
    
    return pd.DataFrame(processed_data)

# Function to export data as CSV
def export_csv(df):
    # Convert dataframe to CSV and allow for downloading
    csv_buffer = StringIO()
    df.to_csv(csv_buffer, index=False)
    csv_file = csv_buffer.getvalue()
    return csv_file

# Display options for selecting data
st.title("BTC/USDT Kline Data Download and Analysis")

symbol = st.selectbox("Select symbol", ["BTCUSDT", "ETHUSDT"])
interval = st.selectbox("Select interval", ["1m", "5m", "15m", "1h", "1d", "1w", "1M"])
start_date = st.date_input("Start date", datetime(2023, 1, 1))
end_date = st.date_input("End date", datetime(2023, 12, 31))

# Download button
if st.button("Download Data"):
    st.write("Downloading data... Please wait.")
    
    kline_data = download_binance_data(symbol, interval, start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d"))
    
    if kline_data:
        df = process_kline_data(kline_data)
        
        st.write("Data downloaded successfully!")
        
        # Displaying the first few rows of the data
        st.write(df.head())
        
        # Option to export the data as CSV
        csv_file = export_csv(df)
        
        # Allow users to download the CSV file
        st.download_button("Download CSV", csv_file, file_name=f"{symbol}_{interval}_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}.csv")

        # Plot the price data
        st.write("Price chart:")
        plt.figure(figsize=(10, 6))
        plt.plot(df['timestamp'], df['close'], label=f'{symbol} {interval} Closing Price')
        plt.title(f'{symbol} Kline Chart ({interval})')
        plt.xlabel('Date')
        plt.ylabel('Price (USDT)')
        plt.grid(True)
        plt.xticks(rotation=45)
        plt.tight_layout()
        st.pyplot()
    else:
        st.error("Failed to download data. Please try again.")

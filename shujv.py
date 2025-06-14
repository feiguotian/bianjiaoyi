import requests
import pandas as pd
from datetime import datetime
import time

# Function to fetch Binance historical Kline data
def download_binance_data(symbol, interval, start_date, end_date):
    base_url = f"https://api.binance.com/api/v3/klines"
    
    # Convert start and end dates to timestamps
    start_timestamp = int(datetime.strptime(start_date, "%Y-%m-%d").timestamp() * 1000)
    end_timestamp = int(datetime.strptime(end_date, "%Y-%m-%d").timestamp() * 1000)
    
    # Parameters for the API request
    params = {
        "symbol": symbol,
        "interval": interval,
        "startTime": start_timestamp,
        "endTime": end_timestamp,
        "limit": 1000  # max limit, can adjust based on the needs
    }

    # List to store all the Kline data
    all_data = []
    
    while True:
        response = requests.get(base_url, params=params)
        if response.status_code == 200:
            data = response.json()
            if len(data) == 0:
                break
            all_data.extend(data)
            
            # Adjust start_time for next batch of data
            params['startTime'] = data[-1][0] + 1  # Next batch starts after the last timestamp
            time.sleep(1)  # Prevent hitting the rate limit
        else:
            print(f"Error: {response.status_code}")
            break

    return all_data

# Function to process and save Kline data
def process_kline_data(kline_data):
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

# Function to save data as CSV
def save_data_to_csv(df, filename):
    df.to_csv(filename, index=False)
    print(f"Data saved to {filename}")

# Parameters for data download
symbol = "BTCUSDT"
interval = "1h"
start_date = "2022-08-01"
end_date = "2025-06-13"

# Download and process the data
kline_data = download_binance_data(symbol, interval, start_date, end_date)

# If data was returned, process and save it
if kline_data:
    df = process_kline_data(kline_data)
    save_data_to_csv(df, "BTCUSDT_1h_data.csv")
else:
    print("No data was returned.")

import requests
import pandas as pd
from datetime import datetime

# 配置参数
symbol = "BTCUSDT"
interval = "1h"
start_time = "2022-08-01"
end_time = "2025-06-14"
limit = 1000  # 每次请求最多1000条数据

# 时间转换为毫秒时间戳
def to_milliseconds(date_str):
    return int(datetime.strptime(date_str, "%Y-%m-%d").timestamp() * 1000)

start_ts = to_milliseconds(start_time)
end_ts = to_milliseconds(end_time)

# 请求数据的函数
def fetch_binance_klines(symbol, interval, start_ts, end_ts):
    url = "https://api.binance.com/api/v3/klines"
    df = pd.DataFrame()
    while start_ts < end_ts:
        params = {
            "symbol": symbol,
            "interval": interval,
            "startTime": start_ts,
            "limit": limit
        }
        response = requests.get(url, params=params)
        data = response.json()
        
        if not data:
            break
        
        temp_df = pd.DataFrame(data, columns=[
            "Open time", "Open", "High", "Low", "Close", "Volume",
            "Close time", "Quote asset volume", "Number of trades",
            "Taker buy base asset volume", "Taker buy quote asset volume", "Ignore"
        ])
        
        temp_df["Open time"] = pd.to_datetime(temp_df["Open time"], unit="ms")
        df = pd.concat([df, temp_df], ignore_index=True)
        
        start_ts = int(temp_df["Open time"].iloc[-1].timestamp() * 1000) + 1
    
    return df[["Open time", "Open", "High", "Low", "Close", "Volume"]]

# 获取数据
btc_df = fetch_binance_klines(symbol, interval, start_ts, end_ts)

# 转换为合适的数据类型
btc_df[["Open", "High", "Low", "Close", "Volume"]] = btc_df[["Open", "High", "Low", "Close", "Volume"]].astype(float)

# 保存为CSV文件
btc_df.to_csv("BTCUSDT_1h_2022-08_to_2025-06.csv", index=False)

print("BTC/USDT数据抓取完成，已保存为：BTCUSDT_1h_2022-08_to_2025-06.csv")

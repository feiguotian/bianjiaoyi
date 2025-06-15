from binance.client import Client
import pandas as pd

# 配置你的API Key和API Secret
api_key = "eVe6isYg7O0sSDJFuPYGoYW6JH2CIhi5lyjL7HVCh3xmTX86AeXvkH8RmRvWI3p8"
api_secret = "e0AB8v4pgGPW3znpEU93aeWjrwxIwpqki8rU5VYKVcFyVOhtoEDjd4sZ0wN5VElJ"  # 注意这里务必填写你的API Secret

# 创建币安客户端
client = Client(api_key, api_secret)

# 定义获取历史K线数据的函数
def fetch_historical_klines(symbol, interval, start_str, end_str):
    klines = client.get_historical_klines(symbol, interval, start_str, end_str)

    df = pd.DataFrame(klines, columns=[
        "Open time", "Open", "High", "Low", "Close", "Volume",
        "Close time", "Quote asset volume", "Number of trades",
        "Taker buy base asset volume", "Taker buy quote asset volume", "Ignore"
    ])

    # 转换数据格式
    df["Open time"] = pd.to_datetime(df["Open time"], unit="ms")
    df["Close time"] = pd.to_datetime(df["Close time"], unit="ms")
    
    df = df[["Open time", "Open", "High", "Low", "Close", "Volume"]]
    df[["Open", "High", "Low", "Close", "Volume"]] = df[["Open", "High", "Low", "Close", "Volume"]].astype(float)

    return df

# 配置参数
symbol = "BTCUSDT"
interval = Client.KLINE_INTERVAL_1HOUR
start_str = "2022-08-01"
end_str = "2025-06-14"

# 获取数据
btc_df = fetch_historical_klines(symbol, interval, start_str, end_str)

# 将数据保存为CSV文件
btc_df.to_csv("BTCUSDT_1h_2022-08_to_2025-06.csv", index=False)

print("数据抓取成功，文件名为：BTCUSDT_1h_2022-08_to_2025-06.csv")

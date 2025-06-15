import requests
import pandas as pd

# 公共API获取K线数据，无需API Key和API Secret
url = "https://api.binance.com/api/v3/klines"
params = {
    "symbol": "BTCUSDT",        # 交易对：BTC/USDT
    "interval": "1h",           # K线周期：1小时
    "limit": 1000,              # 获取最近1000条K线
}

response = requests.get(url, params=params)
data = response.json()

# 将获取的数据转换为DataFrame
df = pd.DataFrame(data, columns=[
    "Open time", "Open", "High", "Low", "Close", "Volume",
    "Close time", "Quote asset volume", "Number of trades",
    "Taker buy base asset volume", "Taker buy quote asset volume", "Ignore"
])

# 将时间转换为可读格式
df["Open time"] = pd.to_datetime(df["Open time"], unit="ms")
df["Close time"] = pd.to_datetime(df["Close time"], unit="ms")

# 保留我们关心的字段
df = df[["Open time", "Open", "High", "Low", "Close", "Volume"]]

# 转换为浮动数据类型
df[["Open", "High", "Low", "Close", "Volume"]] = df[["Open", "High", "Low", "Close", "Volume"]].astype(float)

# 将结果保存为CSV
df.to_csv("BTCUSDT_1h_public_api.csv", index=False)

print("公共API数据已保存为：BTCUSDT_1h_public_api.csv")

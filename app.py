import requests
import pandas as pd

# 公共API获取K线数据，无需API Key和API Secret
url = "https://api.binance.com/api/v3/klines"
params = {
    "symbol": "BTCUSDT",        # 交易对：BTC/USDT
    "interval": "1h",           # K线周期：1小时
    "limit": 1000,              # 获取最近1000条K线
}

# 发送请求
response = requests.get(url, params=params)

# 处理响应数据
if response.status_code == 200:
    data = response.json()

    # 将数据转换为DataFrame
    df = pd.DataFrame(data, columns=[
        "Open time", "Open", "High", "Low", "Close", "Volume",
        "Close time", "Quote asset volume", "Number of trades",
        "Taker buy base asset volume", "Taker buy quote asset volume", "Ignore"
    ])

    # 将时间戳转换为可读格式
    df["Open time"] = pd.to_datetime(df["Open time"], unit="ms")
    df["Close time"] = pd.to_datetime(df["Close time"], unit="ms")

    # 只保留关心的字段
    df = df[["Open time", "Open", "High", "Low", "Close", "Volume"]]

    # 转换为浮动数据类型
    df[["Open", "High", "Low", "Close", "Volume"]] = df[["Open", "High", "Low", "Close", "Volume"]].astype(float)

    # 保存为CSV文件
    df.to_csv("BTCUSDT_1h_public_api.csv", index=False)
    print("数据抓取成功，已保存为：BTCUSDT_1h_public_api.csv")
else:
    print(f"请求失败，状态码：{response.status_code}")

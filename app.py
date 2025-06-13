import streamlit as st
import pandas as pd
import requests
import json

# 读取 API 密钥
def load_api_keys():
    with open('config.json') as f:
        keys = json.load(f)
    return keys['api_key'], keys['api_secret']

# 获取币安历史 K 线数据
def get_binance_ohlcv(symbol, interval='1h', limit=1000):
    url = 'https://api.binance.com/api/v1/klines'
    params = {
        'symbol': symbol,
        'interval': interval,
        'limit': limit
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        ohlcv_data = pd.DataFrame(data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_asset_volume', 'number_of_trades', 'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'])
        ohlcv_data['timestamp'] = pd.to_datetime(ohlcv_data['timestamp'], unit='ms')
        ohlcv_data['close'] = ohlcv_data['close'].astype(float)
        return ohlcv_data
    else:
        st.error(f"请求失败，状态码：{response.status_code}")
        return None

# 主函数：Streamlit 应用
def main():
    st.title("币安 BTC/USDT 历史 K 线数据")

    # 显示输入框来选择交易对和时间间隔
    symbol = st.text_input("交易对", "BTCUSDT")
    interval = st.selectbox("选择时间间隔", ['1m', '5m', '15m', '30m', '1h', '4h', '1d'])

    # 获取并展示数据
    if st.button("获取数据"):
        ohlcv_data = get_binance_ohlcv(symbol, interval)
        
        if ohlcv_data is not None:
            st.write(f"最近 {len(ohlcv_data)} 条 K 线数据：")
            st.dataframe(ohlcv_data)

            # 绘制 K 线图
            st.line_chart(ohlcv_data['close'])

# 运行应用
if __name__ == '__main__':
    main()

import requests
import pandas as pd
import streamlit as st

# 获取 CryptoCompare 历史 K 线数据
def get_cryptocompare_ohlcv(symbol='BTC', vs_currency='USDT', limit=2000):
    url = f'https://min-api.cryptocompare.com/data/v2/histoday'
    params = {
        'fsym': symbol,  # 目标币种，例如 BTC
        'tsym': vs_currency,  # 对比货币，例如 USDT
        'limit': limit,  # 数据条数（最大2000条）
        'toTs': 'current'  # 当前时间
    }

    response = requests.get(url, params=params)
    
    if response.status_code == 200:
        data = response.json()['Data']['Data']
        ohlcv_data = pd.DataFrame(data)
        ohlcv_data['time'] = pd.to_datetime(ohlcv_data['time'], unit='s')
        return ohlcv_data[['time', 'close']]
    else:
        st.error(f"请求失败，状态码：{response.status_code}")
        return None

# 简单的波浪理论分析
def analyze_waves(data):
    peaks = []
    troughs = []
    
    for i in range(1, len(data) - 1):
        if data['close'][i] > data['close'][i-1] and data['close'][i] > data['close'][i+1]:
            peaks.append(i)
        elif data['close'][i] < data['close'][i-1] and data['close'][i] < data['close'][i+1]:
            troughs.append(i)
    
    st.write(f"峰值：{peaks}")
    st.write(f"谷值：{troughs}")
    
    if len(peaks) >= 3 and len(troughs) >= 2:
        wave = "未知"
        if peaks[0] < troughs[0] and peaks[1] > troughs[1] and peaks[2] > troughs[1]:
            wave = "波浪3"
        elif peaks[0] > troughs[0]:
            wave = "波浪1"
        return wave
    else:
        return "数据不足，无法判断"

# Streamlit 界面展示
def main():
    st.title("CryptoCompare BTC/USDT 历史数据与波浪理论分析")
    
    # 用户输入交易对和时间间隔
    symbol = st.text_input("交易对", "BTC")  # 选择加密货币符号，例如 'BTC' 或 'ETH'
    vs_currency = st.text_input("对比货币", "USDT")  # 默认使用 USDT
    limit = st.number_input("获取的最大数据条数", min_value=1, max_value=2000, value=100)
    
    if st.button("获取数据"):
        ohlcv_data = get_cryptocompare_ohlcv(symbol=symbol, vs_currency=vs_currency, limit=limit)
        
        if ohlcv_data is not None:
            st.write(f"最近 {len(ohlcv_data)} 条 K 线数据：")
            st.dataframe(ohlcv_data)

            # 绘制 K 线的收盘价图
            st.line_chart(ohlcv_data['close'])

            # 波浪理论分析
            wave = analyze_waves(ohlcv_data)
            st.write(f"当前处于：{wave} 波")

# 运行应用
if __name__ == '__main__':
    main()

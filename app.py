import requests
import pandas as pd
import streamlit as st

# 获取币安历史 K 线数据
def get_binance_ohlcv(symbol, interval='1h', limit=1000):
    url = 'https://api.binance.com/api/v1/klines'
    params = {
        'symbol': symbol,  # 交易对
        'interval': interval,  # K线周期
        'limit': limit,  # 获取的数据条数
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

# 波浪理论分析：简化版
def analyze_waves(data):
    # 简单识别波浪的高低点
    peaks = []
    troughs = []
    
    for i in range(1, len(data) - 1):
        if data['close'][i] > data['close'][i-1] and data['close'][i] > data['close'][i+1]:
            peaks.append(i)
        elif data['close'][i] < data['close'][i-1] and data['close'][i] < data['close'][i+1]:
            troughs.append(i)
    
    # 打印高低点
    st.write(f"峰值：{peaks}")
    st.write(f"谷值：{troughs}")
    
    # 判断波浪结构（简单版）
    if len(peaks) >= 3 and len(troughs) >= 2:
        # 假设波浪 1, 2, 3, 4, 5 对应于一些基本的规则
        wave = "未知"
        # 简化：如果存在波浪1, 2, 3结构，判断波浪3是否已经完成
        if peaks[0] < troughs[0] and peaks[1] > troughs[1] and peaks[2] > troughs[1]:
            wave = "波浪3"
        elif peaks[0] > troughs[0]:
            wave = "波浪1"
        return wave
    else:
        return "数据不足，无法判断"

# Streamlit 界面展示
def main():
    st.title("币安 BTC/USDT 历史 K 线数据与波浪理论分析")
    
    # 用户输入交易对和时间间隔
    symbol = st.text_input("交易对", "BTCUSDT")
    interval = st.selectbox("选择时间间隔", ['1m', '5m', '15m', '30m', '1h', '4h', '1d'])
    
    if st.button("获取数据"):
        ohlcv_data = get_binance_ohlcv(symbol, interval)
        
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

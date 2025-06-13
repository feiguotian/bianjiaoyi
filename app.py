import requests
import pandas as pd
import streamlit as st

# 获取 CoinGecko 小时级别 K 线数据
def get_coingecko_ohlcv(symbol='bitcoin', vs_currency='usd', days=30):
    url = f'https://api.coingecko.com/api/v3/coins/{symbol}/market_chart'
    params = {
        'vs_currency': vs_currency,
        'days': days,  # 获取过去多少天的数据
        'interval': 'hourly'  # 获取每小时的数据
    }
    
    response = requests.get(url, params=params)
    
    if response.status_code == 200:
        data = response.json()
        ohlcv_data = pd.DataFrame(data['prices'], columns=['timestamp', 'price'])
        ohlcv_data['timestamp'] = pd.to_datetime(ohlcv_data['timestamp'], unit='ms')
        return ohlcv_data
    else:
        st.error(f"请求失败，状态码：{response.status_code}")
        return None

# 识别峰值和谷值的函数
def identify_peaks_and_troughs(prices):
    peaks = []
    troughs = []
    
    for i in range(1, len(prices) - 1):
        if prices[i] > prices[i-1] and prices[i] > prices[i+1]:
            peaks.append(i)
        elif prices[i] < prices[i-1] and prices[i] < prices[i+1]:
            troughs.append(i)
    
    return peaks, troughs

# 简单的波浪推测函数，基于峰值和谷值的相对位置
def predict_wave_structure(peaks, troughs, prices):
    # 确保至少有2个峰值和2个谷值才能进行分析
    if len(peaks) < 2 or len(troughs) < 2:
        return "无法确定波浪阶段，数据不足"
    
    # 检查波浪1和波浪2的模式
    if prices[peaks[0]] > prices[troughs[0]] and prices[troughs[0]] < prices[peaks[1]]:
        # 简单的推测：如果第一个峰值高于第一个谷值，并且第二个峰值高于第二个谷值，则可能处于波浪1
        return "当前可能处于波浪1"
    
    # 检查波浪3的模式：波浪3通常是最强的上涨波段
    if prices[peaks[1]] > prices[troughs[1]] and prices[peaks[1]] > prices[peaks[0]]:
        return "当前可能处于波浪3"
    
    # 检查波浪5的模式：通常与波浪1相似，且波浪5接近波浪3的顶点
    if prices[peaks[2]] > prices[peaks[1]] and prices[peaks[2]] > prices[peaks[0]]:
        return "当前可能处于波浪5"

    return "无法确定具体波浪阶段"

# Streamlit 界面展示
def main():
    st.title("CoinGecko BTC/USDT 小时数据与波浪理论分析")
    
    # 用户输入交易对和时间间隔
    symbol = st.text_input("交易对", "bitcoin")  # 选择加密货币符号，例如 'bitcoin' 或 'ethereum'
    vs_currency = st.text_input("对比货币", "usd")  # 默认使用 USD
    days = st.number_input("获取过去的天数", min_value=1, max_value=365, value=30)
    
    if st.button("获取数据"):
        ohlcv_data = get_coingecko_ohlcv(symbol=symbol, vs_currency=vs_currency, days=days)
        
        if ohlcv_data is not None:
            st.write(f"最近 {len(ohlcv_data)} 条 K 线数据：")
            st.dataframe(ohlcv_data)

            # 绘制 K 线的收盘价图
            st.line_chart(ohlcv_data['price'])

            # 识别波浪的峰值和谷值
            peaks, troughs = identify_peaks_and_troughs(ohlcv_data['price'].values)

            # 波浪分析
            wave_prediction = predict_wave_structure(peaks, troughs, ohlcv_data['price'].values)
            st.write(f"当前处于：{wave_prediction} 波")

# 运行应用
if __name__ == '__main__':
    main()

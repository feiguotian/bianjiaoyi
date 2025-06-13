import requests
import pandas as pd
import streamlit as st

# 获取 CoinGecko 历史 K 线数据
def get_coingecko_ohlcv(symbol='bitcoin', vs_currency='usd', days=30):
    url = f'https://api.coingecko.com/api/v3/coins/{symbol}/market_chart'
    params = {
        'vs_currency': vs_currency,
        'days': days,  # 获取过去多少天的数据
        'interval': 'daily'  # 可以选择 hourly/daily
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

# Streamlit 界面展示
def main():
    st.title("CoinGecko BTC/USDT 历史数据与波浪理论分析")
    
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

# 运行应用
if __name__ == '__main__':
    main()

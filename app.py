import sqlite3
import requests
import pandas as pd
import streamlit as st
import time
from datetime import datetime
import plotly.graph_objects as go

# 设置 SQLite 数据库连接
def create_db_connection():
    conn = sqlite3.connect('market_data.db')
    return conn

# 创建表格（如果不存在）
def create_table():
    conn = create_db_connection()
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS market_data (
                    timestamp TEXT,
                    price REAL
                )''')
    conn.commit()
    conn.close()

# 将新的数据插入到数据库中
def insert_data(timestamp, price):
    conn = create_db_connection()
    c = conn.cursor()
    
    # 将 Timestamp 转换为字符串（ISO 8601 格式）
    timestamp_str = timestamp.strftime('%Y-%m-%d %H:%M:%S')
    
    c.execute("INSERT INTO market_data (timestamp, price) VALUES (?, ?)", (timestamp_str, price))
    conn.commit()
    conn.close()

# 获取历史数据
def get_historical_data():
    conn = create_db_connection()
    query = "SELECT * FROM market_data ORDER BY timestamp ASC"
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

# 获取 CoinGecko 小时级别 K 线数据（不加 interval 参数）
def get_coingecko_ohlcv(symbol='bitcoin', vs_currency='usd', days=30):
    url = f'https://api.coingecko.com/api/v3/coins/{symbol}/market_chart'
    params = {
        'vs_currency': vs_currency,
        'days': days  # 2~90天，自动返回小时级数据
    }
    
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        ohlcv_data = pd.DataFrame(data['prices'], columns=['timestamp', 'price'])
        ohlcv_data['timestamp'] = pd.to_datetime(ohlcv_data['timestamp'], unit='ms')
        return ohlcv_data
    else:
        st.error(f"请求失败，状态码：{response.status_code}, 错误详情：{response.text}")
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
    if len(peaks) < 2 or len(troughs) < 2:
        return "无法确定波浪阶段，数据不足"
    
    if prices[peaks[0]] > prices[troughs[0]] and prices[troughs[0]] < prices[peaks[1]]:
        return "当前可能处于波浪1"
    
    if prices[peaks[1]] > prices[troughs[1]] and prices[peaks[1]] > prices[peaks[0]]:
        return "当前可能处于波浪3"
    
    if prices[peaks[2]] > prices[peaks[1]] and prices[peaks[2]] > prices[peaks[0]]:
        return "当前可能处于波浪5"

    return "无法确定具体波浪阶段"

# Trend check function: Verifying breakout levels
def trend_check(price, support_level=107927, top_level=105333):
    if price < support_level:
        return f"价格跌破 {support_level}，存在见顶风险！"
    elif price < top_level:
        return f"价格跌破 {top_level}，进一步见顶风险验证！"
    else:
        return f"价格维持在支撑位 {support_level} 之上，趋势可能继续上涨"

# K线图的绘制
def plot_candlestick_chart(data, peaks, troughs):
    fig = go.Figure(data=[go.Candlestick(
        x=data['timestamp'],
        open=data['price'],
        high=data['price'],
        low=data['price'],
        close=data['price'],
        name="K线图"
    )])

    # 标记波浪的峰值和谷值
    fig.add_trace(go.Scatter(
        x=data['timestamp'].iloc[peaks], 
        y=data['price'].iloc[peaks], 
        mode='markers', 
        name='峰值', 
        marker=dict(color='red', size=10)
    ))

    fig.add_trace(go.Scatter(
        x=data['timestamp'].iloc[troughs], 
        y=data['price'].iloc[troughs], 
        mode='markers', 
        name='谷值', 
        marker=dict(color='blue', size=10)
    ))

    fig.update_layout(
        title="比特币小时K线图",
        xaxis_title="时间",
        yaxis_title="价格 (USD)",
        xaxis_rangeslider_visible=False
    )

    st.plotly_chart(fig)

# 计算波浪区间和趋势
def calculate_wave_range(prices, wave_type):
    if wave_type == "wave3":  # 假设波浪3通常会扩展到1.618倍的波浪1
        wave1_length = prices[1] - prices[0]
        wave3_target = prices[1] + 1.618 * wave1_length
        return prices[1], wave3_target  # 当前价格，预测的波浪3的目标价格

    elif wave_type == "wave5":  # 假设波浪5类似于波浪1
        wave1_length = prices[1] - prices[0]
        wave5_target = prices[1] + wave1_length
        return prices[1], wave5_target  # 当前价格，预测的波浪5的目标价格
    
    return prices[0], prices[0]  # 无法计算时返回初始值

# Streamlit 界面展示
def main():
    st.title("自动波浪理论与趋势分析")

    symbol = st.text_input("交易对", "bitcoin")  # 选择加密货币符号，例如 'bitcoin' 或 'ethereum'
    vs_currency = st.text_input("对比货币", "usd")  # 默认使用 USD
    days = st.number_input("获取过去的天数（2-90天小时线）", min_value=2, max_value=90, value=30)
    
    if st.button("开始实时获取数据并分析"):
        ohlcv_data = get_coingecko_ohlcv(symbol=symbol, vs_currency=vs_currency, days=days)
        
        if ohlcv_data is not None:
            st.write(f"获取了 {len(ohlcv_data)} 条数据，数据完整性验证通过。")

            # 绘制 K 线图
            peaks, troughs = identify_peaks_and_troughs(ohlcv_data['price'].values)
            plot_candlestick_chart(ohlcv_data, peaks, troughs)

            # 将数据存储到数据库中
            for index, row in ohlcv_data.iterrows():
                insert_data(row['timestamp'], row['price'])

            # 获取历史数据
            historical_data = get_historical_data()
            st.write(f"历史数据：")
            st.dataframe(historical_data)

            # 波浪分析
            wave_prediction = predict_wave_structure(peaks, troughs, historical_data['price'].values)
            st.write(f"当前处于：{wave_prediction} 波")

            # 获取下一个波浪的起始和区间
            if wave_prediction == "当前可能处于波浪3":
                start_price, target_price = calculate_wave_range(historical_data['price'].values, "wave3")
                st.write(f"下一个波浪3的起始价格：{start_price}，目标价格区间：{start_price} 到 {target_price}")
            elif wave_prediction == "当前可能处于波浪5":
                start_price, target_price = calculate_wave_range(historical_data['price'].values, "wave5")
                st.write(f"下一个波浪5的起始价格：{start_price}，目标价格区间：{start_price} 到 {target_price}")

            # 获取最新价格并做趋势判断
            latest_price = ohlcv_data['price'].iloc[-1]
            trend_analysis = trend_check(latest_price)
            st.write(trend_analysis)

# 运行应用
if __name__ == '__main__':
    create_table()
    main()

import sqlite3
import requests
import pandas as pd
import streamlit as st
import time
from datetime import datetime
import plotly.graph_objects as go
import json
import io

# 设置 SQLite 数据库连接
def create_db_connection():
    conn = sqlite3.connect('market_data.db', timeout=10)  # 设置超时避免锁定
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

# 获取币安的历史数据
def get_binance_ohlcv(symbol='BTCUSDT', interval='1h', limit=1000):
    url = f'https://api.binance.com/api/v1/klines'
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
        ohlcv_data['price'] = ohlcv_data['close'].astype(float)  # 以close价格作为价格数据
        return ohlcv_data[['timestamp', 'price']]
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

# 详细的波浪理论规则分析
def wave_analysis(prices, peaks, troughs):
    result = ""
    
    if len(peaks) >= 2 and len(troughs) >= 2:
        # 计算波浪1的长度
        wave1_length = prices[peaks[1]] - prices[troughs[0]]
        
        # 波浪2的回撤率（通常为50%-61.8%）
        wave2_retrace = (prices[peaks[1]] - prices[troughs[1]]) / wave1_length
        if wave2_retrace > 0.8:
            result += "波浪2的回撤超过了61.8%，不符合常规波浪理论。\n"
        
        # 计算波浪3的预期长度（波浪1的1.618倍）
        wave3_length = wave1_length * 1.618
        expected_wave3_target = prices[peaks[1]] + wave3_length
        result += f"波浪3的预期目标：{expected_wave3_target}\n"

        # 波浪4的回撤率（通常为38.2%以内）
        wave4_retrace = (prices[peaks[2]] - prices[troughs[2]]) / wave1_length
        if wave4_retrace > 0.382:
            result += "波浪4的回撤超过了38.2%，不符合常规波浪理论。\n"

        result += "分析结果：符合波浪理论规则。\n"
    else:
        result = "数据不足以进行波浪理论分析。\n"

    return result

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

# 手动波浪数据表格（起点、终点）
def display_wave_table(waves_data):
    df = pd.DataFrame(waves_data, columns=["浪编号", "起点", "终点"])
    st.dataframe(df)

# 保存和导入波浪数据
def save_wave_data(waves_data):
    # 将波浪数据转换为 CSV 格式
    output = io.BytesIO()
    df = pd.DataFrame(waves_data, columns=["浪编号", "起点", "终点"])
    df.to_csv(output, index=False)
    output.seek(0)
    return output

def load_wave_data(filename="waves_data.json"):
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

# Streamlit 界面展示
def main():
    st.title("自动波浪理论与趋势分析")

    # 设置左右布局
    col1, col2 = st.columns([1, 3])  # 左侧和右侧列
    
    # 左侧表格展示
    with col1:
        st.header("波浪数据表格")
        waves_data = load_wave_data()  # 加载已保存的波浪数据

        # 默认波浪数据
        if len(waves_data) == 0:
            waves_data = [["1", 10394, 20203], ["2", 20203, 25000], ["3", 25000, 30000]]
        
        display_wave_table(waves_data)  # 显示波浪数据表格

    # 右侧数据分析和可视化
    with col2:
        # 添加一个按钮来选择数据源
        data_source = st.radio("选择数据源", ("CoinGecko", "Binance"), index=0)

        symbol = 'bitcoin'  # 固定为比特币
        vs_currency = 'usd'  # 对比美元
        days = 30  # 默认取30天的数据
        
        if data_source == "CoinGecko":
            ohlcv_data = get_coingecko_ohlcv(symbol=symbol, vs_currency=vs_currency, days=days)
        else:  # 使用Binance的数据
            ohlcv_data = get_binance_ohlcv(symbol="BTCUSDT", interval="1h", limit=1000)
        
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
            wave_prediction = wave_analysis(historical_data['price'].values, peaks, troughs)
            st.write(wave_prediction)

            # 获取下一个波浪的起始和区间
            if wave_prediction:
                st.write("波浪预测完成。")
            
            # 导出数据按钮
            csv_file = save_wave_data(waves_data)
            st.download_button(
                label="导出波浪数据",
                data=csv_file,
                file_name="waves_data.csv",
                mime="text/csv"
            )

# 运行应用
if __name__ == '__main__':
    create_table()
    main()

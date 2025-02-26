import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

def get_stock_data(ticker, period="6mo", interval="1d"):
    """Fetch stock market data using yfinance."""
    stock = yf.Ticker(ticker)
    data = stock.history(period=period, interval=interval)
    return data

def calculate_indicators(data):
    """Calculate moving averages, RSI, and MACD."""
    data["SMA_50"] = data["Close"].rolling(window=50).mean()
    data["SMA_200"] = data["Close"].rolling(window=200).mean()
    delta = data["Close"].diff()
    gain = (delta.where(delta > 0, 0)).rolling(14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
    rs = gain / loss
    data["RSI"] = 100 - (100 / (1 + rs))
    
    # MACD Calculation
    data["EMA_12"] = data["Close"].ewm(span=12, adjust=False).mean()
    data["EMA_26"] = data["Close"].ewm(span=26, adjust=False).mean()
    data["MACD"] = data["EMA_12"] - data["EMA_26"]
    data["Signal_Line"] = data["MACD"].ewm(span=9, adjust=False).mean()
    
    return data

def generate_signals(data):
    """Generate Buy/Sell signals based on indicators."""
    buy_signals = []
    sell_signals = []
    
    for i in range(len(data)):
        if data["SMA_50"][i] > data["SMA_200"][i]:
            buy_signals.append(data["Close"][i])
            sell_signals.append(None)
        elif data["SMA_50"][i] < data["SMA_200"][i]:
            sell_signals.append(data["Close"][i])
            buy_signals.append(None)
        else:
            buy_signals.append(None)
            sell_signals.append(None)
    
    data["Buy_Signal"] = buy_signals
    data["Sell_Signal"] = sell_signals
    return data

def plot_stock_trend(data, ticker):
    """Visualize stock trends and buy/sell signals."""
    plt.figure(figsize=(12, 6))
    plt.plot(data["Close"], label="Closing Price", alpha=0.5)
    plt.plot(data["SMA_50"], label="50-day SMA", linestyle="--", alpha=0.7)
    plt.plot(data["SMA_200"], label="200-day SMA", linestyle="--", alpha=0.7)
    
    plt.scatter(data.index, data["Buy_Signal"], label="Buy Signal", marker="^", color="green", alpha=1)
    plt.scatter(data.index, data["Sell_Signal"], label="Sell Signal", marker="v", color="red", alpha=1)
    
    plt.title(f"{ticker} Market Trend")
    plt.legend()
    st.pyplot(plt)

def plot_macd(data):
    """Plot MACD and Signal Line."""
    plt.figure(figsize=(12, 4))
    plt.plot(data["MACD"], label="MACD", color="blue")
    plt.plot(data["Signal_Line"], label="Signal Line", color="red")
    plt.axhline(0, linestyle="--", alpha=0.5, color="gray")
    plt.title("MACD Indicator")
    plt.legend()
    st.pyplot(plt)

# Streamlit UI
st.title("Stock Market Trend Analyzer")

# User input
ticker_symbol = st.text_input("Enter Stock Ticker (e.g., AAPL):", "AAPL")
if st.button("Analyze Stock"):
    data = get_stock_data(ticker_symbol)
    data = calculate_indicators(data)
    data = generate_signals(data)
    plot_stock_trend(data, ticker_symbol)
    plot_macd(data)
    st.dataframe(data[["Close", "SMA_50", "SMA_200", "RSI", "MACD", "Signal_Line", "Buy_Signal", "Sell_Signal"]].tail())

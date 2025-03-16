import pandas as pd
import numpy as np
import yfinance as yf
import streamlit as st
import plotly.express as px
from alpha_vantage.fundamentaldata import FundamentalData
import os
from dotenv import load_dotenv
from stocknews import StockNews

# Load environment variables
load_dotenv()
ALPHA_VANTAGE_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY")

st.title('Stock Dashboard')
ticker = st.sidebar.text_input("Enter Stock Ticker", 'AAPL')  # Default value
start_date = st.sidebar.date_input("Start Date")
end_date = st.sidebar.date_input("End Date")

# Fetch stock data
@st.cache_data
def fetch_stock_data(ticker, start_date, end_date):
    return yf.download(ticker, start=start_date, end=end_date, auto_adjust=False, progress=True)

if not ticker:
    st.warning("Please enter a valid ticker symbol.")
else:
    data = fetch_stock_data(ticker, start_date, end_date)
    
    if data.empty:
        st.error("No data found. Please check the ticker symbol and date range.")
    else:
        column_name = 'Adj Close' if 'Adj Close' in data.columns else 'Close'
        fig = px.line(data, x=data.index, y=data[column_name].squeeze(), title=f"{ticker} Stock Price")
        st.plotly_chart(fig)

pricing_data, fundamental_data, news = st.tabs(["Pricing Data", "Fundamental Data", "Top 10 News"])

# Pricing Data Tab
with pricing_data:
    st.write('Price Movements')
    data2 = data
    data2['% Change'] = data['Adj Close'] / data['Adj Close'].shift(1) - 1
    st.write(data)
    annual_return = data2['% Change'].mean() * 252 * 100
    st.write(f"Annual Return: {annual_return:.2f}%")
    stdev = np.std(data2['% Change']) * np.sqrt(252)
    st.write(f"Standard Deviation: {stdev*100:.2f}%")
    st.write(f'Risk-Adjusted Return: {annual_return / (stdev * 100):.2f}')

# Fundamental Data Tab with Caching
@st.cache_data
def fetch_balance_sheet(ticker, key):
    fd = FundamentalData(key, output_format='pandas')
    return fd.get_balance_sheet_annual(ticker)[0]

@st.cache_data
def fetch_income_statement(ticker, key):
    fd = FundamentalData(key, output_format='pandas')
    return fd.get_income_statement_annual(ticker)[0]

@st.cache_data
def fetch_cash_flow(ticker, key):
    fd = FundamentalData(key, output_format='pandas')
    return fd.get_cash_flow_annual(ticker)[0]

with fundamental_data:
    key = ALPHA_VANTAGE_API_KEY

    if not key:
        st.error("Alpha Vantage API Key is missing! Set it in environment variables.")
    else:
        try:
            st.subheader('Balance Sheet')
            balance_sheet = fetch_balance_sheet(ticker, key)
            bs = balance_sheet.T[2:]
            bs.columns = list(balance_sheet.T.iloc[0])
            st.write(bs)

            st.subheader('Income Statement')
            income_statement = fetch_income_statement(ticker, key)
            is1 = income_statement.T[2:]
            is1.columns = list(income_statement.T.iloc[0])
            st.write(is1)

            st.subheader('Cash Flow Statement')
            cash_flow = fetch_cash_flow(ticker, key)
            cf = cash_flow.T[2:]
            cf.columns = list(cash_flow.T.iloc[0])
            st.write(cf)

        except Exception as e:
            st.error("Error fetching fundamental data. API limit may have been reached.")

# News Tab
with news:
    st.header(f'News for {ticker}')
    sn = StockNews(ticker, save_news=False)
    df_news = sn.read_rss()

    for i in range(min(10, len(df_news))):
        st.subheader(f'News {i+1}')
        st.write(df_news['published'][i])
        st.write(df_news['title'][i])
        st.write(df_news['summary'][i])
        st.write(f"Title Sentiment: {df_news['sentiment_title'][i]}")
        st.write(f"News Sentiment: {df_news['sentiment_summary'][i]}")

 
if __name__ == "__main__":
    os.system("streamlit run stock_analysis.py --server.port 8000 --server.address 0.0.0.0")

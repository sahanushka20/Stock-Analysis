import pandas as pd
import numpy as np
import yfinance as yf
import streamlit as st
import plotly.express as px

st.title('Stock Dashboard')
ticker = st.sidebar.text_input("Enter Stock Ticker", 'AAPL' )  # Default value
start_date = st.sidebar.date_input("Start Date")
end_date = st.sidebar.date_input("End Date")

 

# Fetch stock data
if not ticker:
    st.warning("Please enter a valid ticker symbol.")
else:
    data = yf.download(ticker, start=start_date, end=end_date, auto_adjust=False, progress=True)


    if data.empty:
        st.error("No data found. Please check the ticker symbol and date range.")
    else:
         

        # Use 'Adj Close' if available, otherwise fall back to 'Close'
       column_name = 'Adj Close' if 'Adj Close' in data.columns else 'Close'
       if column_name in data.columns:
            fig = px.line(data, x=data.index, y=data[column_name].squeeze(), title=f"{ticker} Stock Price")
            st.plotly_chart(fig)
       else:
            st.error("No price data found for the selected stock.")
pricing_data, fundamental_data, news = st.tabs(["Pricing Data", "Fundamental Data", "Top 10 News" ])

with pricing_data:
    st.write('Price Movements')
    data2 = data
    data2['% Change'] = data['Adj Close'] / data['Adj Close'].shift(1) - 1
    st.write(data)
    annual_return = data2['% Change'].mean()*252*100
    st.write(f"Annual Return: {annual_return:.2f}%")
    stdev = np.std(data2['% Change'])*np.sqrt(252)
    st.write(f"Standard Deviation: {stdev*100: .2f}%")
    st.write('Risk Adj. Return is ', annual_return/(stdev*100))

from alpha_vantage.fundamentaldata import FundamentalData
import os
from dotenv import load_dotenv
load_dotenv()
with fundamental_data:
    key = os.getenv("ALPHA_VANTAGE_API_KEY")
    fd = FundamentalData(key, output_format = 'pandas')
    st.subheader('Balance Sheet')
    balance_sheet = fd.get_balance_sheet_annual(ticker)[0]
    bs = balance_sheet.T[2:]
    bs.columns = list(balance_sheet.T.iloc[0])
    st.write(bs)
    st.subheader('Income Statement')
    income_statement = fd.get_income_statement_annual(ticker) [0]
    is1 = income_statement.T[2:]
    is1.columns = list(income_statement.T.iloc[0])
    st.write(is1)
    st.subheader('Cash Flow Statement')
    cash_flow = fd.get_cash_flow_annual (ticker)[0]
    cf = cash_flow.T[2:]
    cf.columns = list(cash_flow.T.iloc[0])
    st.write(cf)
 

from stocknews import StockNews

with news:
    st.header(f'News of {ticker}')
    sn = StockNews(ticker, save_news=False)
    df_news = sn.read_rss()
    for i in range(10):
        st.subheader(f'News {i+1}')
        st.write(df_news['published'][i])
        st.write(df_news['title'][i]) 
        st.write(df_news['summary'][i])
        title_sentiment = df_news['sentiment_title'][i]
        st.write(f'Title Sentiment {title_sentiment}')
        news_sentiment = df_news['sentiment_summary'][i]
        st.write(f'News Sentiment {news_sentiment}')


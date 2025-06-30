import logging
import requests
from time import sleep
from datetime import datetime, timedelta
from nsepy import get_history
import yfinance as yf
from alpha_vantage.timeseries import TimeSeries
import pandas as pd
import time

API_KEY = os.getenv("ALPHAVANTAGE_KEY")  # Store as env variable in production

def fetch_alpha_data(symbol, interval='daily', outputsize='compact'):
    try:
        ts = TimeSeries(key=API_KEY, output_format='pandas')
        data, meta = ts.get_daily(symbol=symbol, outputsize=outputsize)
        data = data.rename(columns={
            '1. open': 'Open',
            '2. high': 'High',
            '3. low': 'Low',
            '4. close': 'Close',
            '5. volume': 'Volume'
        })
        data.index = pd.to_datetime(data.index)
        return data
    except Exception as e:
        print(f"[❌] AlphaVantage error for {symbol}: {e}")
        return None
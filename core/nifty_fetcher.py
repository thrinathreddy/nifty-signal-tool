import logging
import requests
from time import sleep
from datetime import datetime, timedelta
from nsepy import get_history
import yfinance as yf
from alpha_vantage.timeseries import TimeSeries
import pandas as pd
import time

API_KEY = "FDTDZQSBN1KGDPOC"  # Store as env variable in production

def fetch_data(symbol, interval='daily', outputsize='compact'):
    try:
        ts = TimeSeries(key=API_KEY, output_format='pandas')
        print("data start")
        data, meta = ts.get_daily(symbol=symbol, outputsize=outputsize)
        print("data start2")
        data = data.rename(columns={
            '1. open': 'Open',
            '2. high': 'High',
            '3. low': 'Low',
            '4. close': 'Close',
            '5. volume': 'Volume'
        })
        print("data start3")
        data.index = pd.to_datetime(data.index)
        print("data start4")
        print(data)
        return data
    except Exception as e:
        print(f"[❌] AlphaVantage error for {symbol}: {e}")
        return None
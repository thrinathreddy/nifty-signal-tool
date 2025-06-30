import yfinance as yf

def fetch_data(symbol, period="6mo", interval="1d"):
    return yf.download(symbol, period=period, interval=interval)

import yfinance as yf
import requests
import time

def get_fundamentals(symbol):
    try:
        stock = yf.Ticker(symbol)
        fin = stock.info
        print(f"\n{symbol} info keys:\n", fin.keys())
        roe = fin.get('returnOnEquity')
        debt_equity = fin.get('debtToEquity')
        eps_growth = fin.get('earningsGrowth')

        # If all three are missing, treat as unavailable
        if roe is None and debt_equity is None and eps_growth is None:
            raise ValueError("Missing expected financial data")

        return roe or 0, debt_equity or 0, eps_growth or 0

    except Exception as e:
        print(f"[❌] fundamental error for {symbol}: {e}")
        return 0, 0, 0

def evaluate_fundamentals(roe, de, eps):
    if roe > 0.15 and de < 100 and eps > 0.1:
        return "LONG_TERM_BUY"
    return "HOLD"

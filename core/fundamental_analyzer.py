import requests

def get_fundamentals(symbol):
    url = f"https://query1.finance.yahoo.com/v10/finance/quoteSummary/{symbol}?modules=financialData"
    res = requests.get(url)
    try:
        fin = res.json()['quoteSummary']['result'][0]['financialData']
        roe = fin.get('returnOnEquity', {}).get('raw', 0)
        debt_equity = fin.get('debtToEquity', {}).get('raw', 0)
        eps_growth = fin.get('earningsGrowth', {}).get('raw', 0)
        return roe, debt_equity, eps_growth
    except:
        print(f"[❌] fundamental error for {symbol}: {e}")
        return 0, 0, 0

def evaluate_fundamentals(roe, de, eps):
    if roe > 0.15 and de < 100 and eps > 0.1:
        return "LONG_TERM_BUY"
    return "HOLD"

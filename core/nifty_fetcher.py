from nsepy import get_history
import datetime
import requests

def fetch_data(symbol, start=None, end=None):
    if start is None:
        start = datetime.date.today() - datetime.timedelta(days=180)
    if end is None:
        end = datetime.date.today()

    try:
        # Monkey-patch headers
        requests.defaults.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)'
        })
        df = get_history(symbol=symbol, start=start, end=end)
        print(df)
        if df.empty:
            print(f"[⚠️] No data for {symbol}")
            return None
        return df
    except Exception as e:
        print(f"[❌] Error fetching data for {symbol}: {e}")
        return None

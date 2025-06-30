from nsepy import get_history
import datetime

def fetch_nse_data(symbol, start=None, end=None):
    if start is None:
        start = datetime.date.today() - datetime.timedelta(days=180)
    if end is None:
        end = datetime.date.today()

    try:
        df = get_history(symbol=symbol, start=start, end=end)
        if df.empty:
            print(f"[⚠️] No data for {symbol}")
            return None
        return df
    except Exception as e:
        print(f"[❌] Error fetching data for {symbol}: {e}")
        return None

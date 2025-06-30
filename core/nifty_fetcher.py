from nsepy import get_history
import datetime
import requests


# Patch requests.get to add headers
_real_get = requests.get

def custom_get(*args, **kwargs):
    headers = kwargs.pop("headers", {})
    headers["User-Agent"] = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    )
    kwargs["headers"] = headers
    return _real_get(*args, **kwargs)

requests.get = custom_get  # Monkey-patch requests.get

def fetch_data(symbol, start=None, end=None):
    if start is None:
        start = datetime.date.today() - datetime.timedelta(days=180)
    if end is None:
        end = datetime.date.today()

    try:
        df = get_history(symbol=symbol, start=start, end=end)
        print(df)
        if df.empty:
            print(f"[⚠️] No data for {symbol}")
            return None
        return df
    except Exception as e:
        print(f"[❌] Error fetching data for {symbol}: {e}")
        return None

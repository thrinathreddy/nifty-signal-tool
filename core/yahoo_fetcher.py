import logging
import requests
import pandas as pd
from time import sleep
from datetime import datetime, timedelta
import yfinance as yf

logging.basicConfig(level=logging.INFO)
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
def yahoo_fetch_data(symbol, days=180, retries=3, delay=2, period="12mo", interval="1d"):
    """
    Fetch historical stock data using nsepy with retry logic.
    
    :param symbol: NSE stock symbol (e.g., 'RELIANCE', 'TCS')
    :param days: Number of past days to fetch
    :param retries: Number of retry attempts
    :param delay: Delay (in seconds) between retries
    :return: DataFrame with historical data or None
    """
    try:
        end = datetime.today()
        start = end - timedelta(days=days)

        try:
            data = yf.download(symbol+".NS", start=start,
    end=end, interval=interval, auto_adjust=True, progress=False, threads=False)
            if data is not None and not data.empty:
                logging.info(f"[{symbol}] ✅ Data fetched successfully with {len(data)} rows.")
                return data
            else:
                logging.warning(f"[{symbol}] ⚠️ Empty data on attempt . Retrying...")
        except Exception as e:
            logging.error(f"[{symbol}] ❌ Exception on attempt : {e}")

        logging.error(f"[{symbol}] ❌ Failed to fetch data after {retries} attempts.")
        return None

    except Exception as e:
        logging.error(f"[{symbol}] ❌ Unexpected error in fetch_data: {e}")
        return None

def get_open_price(symbol, base_date):
    try:
        ticker = yf.Ticker(symbol+".NS")
        df = ticker.history(interval="30m", period="1d")
        print(df)
        # Reset index for easier handling
        df = df.reset_index()
        # Extract timezone from the data
        data_tz = df['Datetime'].dt.tz

        # Get today in the same timezone
        today = pd.Timestamp.now(tz=data_tz).normalize()
        print(today)
        # Get the first row from today
        today_data = df[df['Datetime'].dt.normalize() == today]

        if not today_data.empty:
            open_time = today_data.iloc[0]['Datetime']
            open_price = today_data.iloc[0]['Open']
            print(f"Today's Open Time: {open_time}")
            print(f"Today's Open Price: {open_price}")
            return open_price
        else:
            print("No data available for today.")
        return None
    except Exception as e:
        print(f"[❌] Failed price for {symbol}: {e}")
        return None

def get_intraday_range(symbol, date_obj):
    start = date_obj.strftime("%Y-%m-%d")
    end = (date_obj + timedelta(days=1)).strftime("%Y-%m-%d")  # yfinance needs next day

    data = yf.download(
        symbol+".NS",
        start=start,
        end=end,
        interval="5m",  # or '15m'
        progress=False,
        prepost=False,
        threads=False
    )

    if data.empty:
        print(f"[❌] No intraday data for {symbol} on {start}")
        return None

    intraday_high = data["High"].max()
    intraday_low = data["Low"].min()
    # Reset index for easier handling
    df = data.reset_index()
    # Extract timezone from the data
    data_tz = df['Datetime'].dt.tz
    # Get today in the same timezone
    current_day = pd.Timestamp(start, tz=data_tz).normalize().date()
    print(current_day)
    today_data = df[df['Datetime'].dt.normalize() == current_day]
    open_price = today_data.iloc[0]['Open']

    return {"open": round(open_price, 2),"high": round(intraday_high, 2), "low": round(intraday_low, 2)}
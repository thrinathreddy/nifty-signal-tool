import yfinance as yf
from nsepy import get_history
import logging
from time import sleep
import datetime

logging.basicConfig(level=logging.INFO)

def fetch_data(symbol, period="6mo", interval="1d", retries=3, delay=2):
    """
    Download data for a symbol with retries and error handling.
    """
    for attempt in range(1, retries + 1):
        try:
            if start is None:
                start = datetime.date.today() - datetime.timedelta(days=180)
            if end is None:
                end = datetime.date.today()
            data = get_history(symbol=symbol, start=start, end=end)
            logging.warning(data)
            if data is not None and not data.empty:
                logging.warning(f"[{symbol}] not empty data")
                return data
            else:
                logging.warning(f"[{symbol}] Empty data on attempt {attempt}. Retrying...")
        except Exception as e:
            logging.error(f"[{symbol}] Exception on attempt {attempt}: {e}")

        sleep(delay)

    logging.error(f"[{symbol}] Failed to fetch data after {retries} attempts.")
    return None
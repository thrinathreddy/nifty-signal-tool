import yfinance as yf
import logging
from time import sleep

logging.basicConfig(level=logging.INFO)

def fetch_data(symbol, period="6mo", interval="1d", retries=3, delay=2):
    """
    Download data for a symbol with retries and error handling.
    """
    for attempt in range(1, retries + 1):
        try:
            data = yf.download(symbol, period=period, interval=interval, progress=False, threads=False)
            if data is not None and not data.empty:
                return data
            else:
                logging.warning(f"[{symbol}] Empty data on attempt {attempt}. Retrying...")
        except Exception as e:
            logging.error(f"[{symbol}] Exception on attempt {attempt}: {e}")

        sleep(delay)

    logging.error(f"[{symbol}] Failed to fetch data after {retries} attempts.")
    return None
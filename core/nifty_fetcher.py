import yfinance as yf
from nsepy import get_history
import logging
from time import sleep
from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO)

def fetch_data(symbol, days=180):
    try:
        end = datetime.today()
        start = end - timedelta(days=days)
        """
        Download data for a symbol with retries and error handling.
        """

        for attempt in range(1, retries + 1):
            try:
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
    except Exception as e:
    logging.error(f"Exception: {e}")
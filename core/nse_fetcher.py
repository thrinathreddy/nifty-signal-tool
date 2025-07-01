import logging
import requests
from time import sleep
from datetime import datetime, timedelta
from nsepy import get_history

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
def nse_fetch_data(symbol, days=180, retries=3, delay=2):
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

        for attempt in range(1, retries + 1):
            try:
                data = get_history(symbol=symbol, start=start, end=end)
                if data is not None and not data.empty:
                    logging.info(f"[{symbol}] ✅ Data fetched successfully with {len(data)} rows.")
                    return data
                else:
                    logging.warning(f"[{symbol}] ⚠️ Empty data on attempt {attempt}. Retrying...")
            except Exception as e:
                logging.error(f"[{symbol}] ❌ Exception on attempt {attempt}: {e}")
            sleep(delay)

        logging.error(f"[{symbol}] ❌ Failed to fetch data after {retries} attempts.")
        return None

    except Exception as e:
        logging.error(f"[{symbol}] ❌ Unexpected error in fetch_data: {e}")
        return None
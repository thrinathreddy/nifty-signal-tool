import sys
import os
import time

from core.marketSentiment_analyzer import get_or_cache_sentiment

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from core.nifty_fetcher import fetch_data
from core.nse_fetcher import nse_fetch_data
from core.yahoo_fetcher import yahoo_fetch_data
from core.indicators import apply_indicators
from core.strategy import generate_signal
from core.db_handler import save_signal
from core.fundamental_analyzer import get_fundamentals, evaluate_fundamentals
from strategies.stockSymbols import STOCKS
import logging
logging.basicConfig(level=logging.INFO)
def run_scan():
    print("inside run scan")
    for name, symbol in STOCKS.items():
        try:
            #df1 = nse_fetch_data(symbol)
            df = yahoo_fetch_data(symbol)
            #df = fetch_data(symbol+".BSE")
            if df is None or df.empty:
                continue
            # After downloading or loading your DataFrame
            logging.info("downloaded data...")
            df.columns = df.columns.get_level_values(0)
            if df["Volume"].mean() < 100000:
                print(f"⚠️ Skipping {symbol} due to low avg volume: {df['Volume'].mean():,.0f}")
                return []
            logging.info(f"✅ Columns after flatten: {df.columns.tolist()}")
            logging.info("📊 Applying indicators...")
            df = apply_indicators(df)
            logging.info("✅ Indicators applied.")

            logging.info("📈 Generating signal...")
            signal = generate_signal(df)
            logging.info(f"✅ Signal generated: {signal}")
            sentiment = get_or_cache_sentiment(symbol)
            logging.info(f"✅ Sentiment generated: {sentiment}")
            if signal == "BUY":
                save_signal(symbol, signal, sentiment)

            # also check long-term signal
            data1 = get_fundamentals(symbol)
            print("<UNK> Data fetched...")
            print(data1)
            ltsignal = evaluate_fundamentals(data1)
            if ltsignal == "LONG_TERM_BUY":
                save_signal(symbol, ltsignal, sentiment)
            time.sleep(0.5)  # Sleep to avoid API throttling
        except Exception as e:
            print(f"Error with {symbol}: {e}")


if __name__ == "__main__":
    run_scan()

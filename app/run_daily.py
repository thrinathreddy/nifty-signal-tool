import sys
import os

from core.marketSentiment_analyzer import get_or_cache_sentiment

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from core.nifty_fetcher import fetch_data
from core.nse_fetcher import nse_fetch_data
from core.yahoo_fetcher import yahoo_fetch_data
from core.indicators import apply_indicators
from core.strategy import generate_signal
from core.db_handler import save_signal
from core.fundamental_analyzer import get_fundamentals, evaluate_fundamentals
import logging
logging.basicConfig(level=logging.INFO)
nifty50 = ["ADANIENT", "ADANIPORTS", "APOLLOHOSP", "ASIANPAINT", "AXISBANK", "BAJAJ‑AUTO", "BAJFINANCE", "BAJAJFINSV", "BEL", "BHARTIARTL", "CIPLA", "COALINDIA", "DRREDDY", "EICHERMOT", "ETERNAL", "GRASIM", "HCLTECH", "HDFCBANK", "HDFCLIFE", "HEROMOTOCO", "HINDALCO", "HINDUNILVR", "ICICIBANK", "INDUSINDBK", "INFY", "ITC", "JIOFIN", "JSWSTEEL", "KOTAKBANK", "LT", "M&M", "MARUTI", "NESTLEIND", "NTPC", "ONGC", "POWERGRID", "RELIANCE", "SBILIFE", "SHRIRAMFIN", "SBIN", "SUNPHARMA", "TCS", "TATACONSUM", "TATAMOTORS", "TATASTEEL", "TECHM", "TITAN", "TRENT", "ULTRACEMCO", "WIPRO"] # sample list
def run_scan():
    print("inside run scan")
    for symbol in nifty50:
        try:
            #df1 = nse_fetch_data(symbol)
            df = yahoo_fetch_data(symbol)
            #df = fetch_data(symbol+".BSE")
            if df is None or df.empty:
                continue
            # After downloading or loading your DataFrame
            logging.info("downloaded data...")
            df.columns = df.columns.get_level_values(0)
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
            roe, de, eps = get_fundamentals(symbol+".NS")
            ltsignal = evaluate_fundamentals(roe, de, eps)
            if ltsignal == "LONG_TERM_BUY":
                save_signal(symbol, ltsignal, sentiment)

        except Exception as e:
            print(f"Error with {symbol}: {e}")


if __name__ == "__main__":
    run_scan()

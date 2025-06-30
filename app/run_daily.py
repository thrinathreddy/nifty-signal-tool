import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from core.nifty_fetcher import fetch_data
from core.indicators import apply_indicators
from core.strategy import generate_signal
from core.db_handler import save_signal
from core.fundamental_analyzer import get_fundamentals, evaluate_fundamentals

nifty50 = ["RELIANCE", "TCS", "INFY", "HDFCBANK"] # sample list
def run_scan():
    for symbol in nifty50:
        try:
            df = fetch_data(symbol)
            if df is None or df.empty:
                continue
            df = apply_indicators(df)
            signal = generate_signal(df)
            if signal == "BUY":
                save_signal(symbol, signal)

            # also check long-term signal
            roe, de, eps = get_fundamentals(symbol)
            ltsignal = evaluate_fundamentals(roe, de, eps)
            if ltsignal == "LONG_TERM_BUY":
                save_signal(symbol, ltsignal)

        except Exception as e:
            print(f"Error with {symbol}: {e}")


if __name__ == "__main__":
    run_scan()

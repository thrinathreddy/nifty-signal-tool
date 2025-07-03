import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from core.getSignals import process_today_buy_signals, process_today_sell_signals

import logging
from datetime import date, timedelta
logging.basicConfig(level=logging.INFO)
def run_scan2():
    print("inside run scan2")
    try:
        logging.info("📈 Generating buys...")
        process_today_buy_signals()
    except Exception as e:
        print(f"Error : {e}")
    try:
        logging.info("📈 Generating sells...")
        process_today_sell_signals()
    except Exception as e:
        print(f"Error : {e}")


if __name__ == "__main__":
    run_scan2()

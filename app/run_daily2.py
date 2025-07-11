import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from core.getSignals import process_today_buy_signals, check_target_stoploss

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
        check_target_stoploss()
    except Exception as e:
        print(f"Error : {e}")



if __name__ == "__main__":
    run_scan2()

from datetime import date, timedelta
from core.db_handler import (get_today_buy_signals, insert_trade_buy, get_today_sell_signals,
                             close_trade_sell, getOpentrades)
from core.yahoo_fetcher import get_open_price, get_intraday_range
def process_today_buy_signals():
    signal_date = date.today() - timedelta(days=1)
    signals = get_today_buy_signals(signal_date)

    for entry in signals:
        symbol = entry['symbol']
        buy_type = entry['type']

        buy_price = get_open_price(symbol, date.today())
        if buy_price:
            insert_trade_buy(symbol, signal_date, buy_price, buy_type)
        else:
            print(f"[❌] Could not fetch price for {symbol}")


def check_target_stoploss():
    # Step 1: Get open trades from Supabase
    open_trades = getOpentrades()

    for trade in open_trades:
        symbol = trade["symbol"]
        buy_price = float(trade["buy_price"])
        buy_type = trade["buy_type"]
        trade_id = trade["id"]

        # Step 2: Define target and stop-loss
        if buy_type == "BUY":
            target = round(buy_price * 1.02, 2)
            stop = round(buy_price * 0.99, 2)
        else:  # LONG_TERM_BUY
            target = round(buy_price * 1.02, 2)
            stop = round(buy_price * 0.98, 2)

        # Step 3: Get today's intraday high/low
        price_info = get_intraday_range(symbol, date.today())
        if not price_info:
            print(f"[❌] No price info for {symbol}")
            continue

        high = price_info["high"]
        low = price_info["low"]

        # Step 4: Check if target or stop was hit
        if high >= target:
            close_trade_sell(symbol, buy_type, date.today(), target)
            print(f"[🏁] Target hit for {symbol} @ {target}")
        elif low <= stop:
            close_trade_sell(symbol, buy_type, date.today(), stop)
            print(f"[⚠️] Stop-loss hit for {symbol} @ {stop}")
        print(f"[🏁] Target not hit for {symbol}")
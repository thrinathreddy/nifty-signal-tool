from datetime import date, timedelta
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from core.db_handler import get_today_buy_signals, insert_trade_buy, get_today_sell_signals, close_trade_sell
from core.yahoo_fetcher import get_open_price
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


def process_today_sell_signals():
    signal_date = date.today() - timedelta(days=1)
    sell_signals = get_today_sell_signals(signal_date)

    for entry in sell_signals:
        symbol = entry['symbol']
        sell_type = entry['type']
        sell_price = get_open_price(symbol, date.today())
        if sell_price:
            if sell_type == 'SELL':
                close_trade_sell(symbol, 'BUY', signal_date, sell_price)
            else:
                close_trade_sell(symbol, 'LONG_TERM_BUY', signal_date, sell_price)
            break  # Close only one open trade per signal
        else:
            print(f"[❌] No price for {symbol}")
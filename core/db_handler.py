from supabase import create_client
import os
from datetime import date, timedelta

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def save_signal(symbol, signal_type, market_sentiment):
    today = str(date.today())

    # First, check if this signal already exists
    existing = supabase.table("signals") \
        .select("*") \
        .eq("symbol", symbol) \
        .eq("date", today) \
        .eq("type", signal_type) \
        .execute()

    if existing.data and len(existing.data) > 0:
        print(f"[⚠️] Signal already exists for {symbol} ({signal_type}) on {today}")
        return

    # Insert only if not already present
    supabase.table("signals").insert({
        "symbol": symbol,
        "date": today,
        "type": signal_type,
        "market_sentiment": market_sentiment
    }).execute()

    print(f"[✅] Signal saved: {symbol} ({signal_type}) on {today}")

def get_signals():
    response = supabase.table("signals").select("*").order("date", desc=True).execute()
    return response.data
def get_signal(symbol, today, signal_type):
    result = supabase.table("signals") \
        .select("market_sentiment") \
        .eq("symbol", symbol) \
        .eq("date", today) \
        .eq("type", signal_type) \
        .execute()
    return result

def insert_trade_buy(symbol, signal_date, buy_price, buy_type):
    buy_trade_date = signal_date + timedelta(days=1)
    today_str = signal_date.isoformat()

    # 1. Check if an OPEN trade already exists for the symbol
    existing = supabase.table("trade_log") \
        .select("id") \
        .eq("symbol", symbol) \
        .eq("status", "OPEN") \
        .eq("buy_type", buy_type) \
        .execute()

    if existing.data and len(existing.data) > 0:
        print(f"[⚠️] Trade already open for {symbol}")
        return

    # 2. Insert the BUY trade
    result = supabase.table("trade_log").insert({
        "symbol": symbol,
        "buy_signal_date": signal_date.isoformat(),
        "buy_trade_date": buy_trade_date.isoformat(),
        "buy_price": buy_price,
        "buy_type": buy_type,
        "status": "OPEN"
    }).execute()

    print(f"[✅] BUY trade logged: {symbol} ({buy_type}) @ {buy_price}")

def close_trade_sell(symbol, buy_type, sell_signal_date, sell_price):
    sell_trade_date = sell_signal_date + timedelta(days=1)

    # 1. Fetch open trade with matching buy_type
    result = supabase.table("trade_log") \
        .select("id, buy_price") \
        .eq("symbol", symbol) \
        .eq("buy_type", buy_type) \
        .eq("status", "OPEN") \
        .limit(1) \
        .execute()

    if not result.data or len(result.data) == 0:
        print(f"[❌] No open trade found for {symbol} with type {buy_type}")
        return

    trade = result.data[0]
    trade_id = trade['id']
    buy_price = float(trade['buy_price'])
    pnl = round(sell_price - buy_price, 2)

    # 2. Update trade
    supabase.table("trade_log") \
        .update({
            "sell_signal_date": sell_signal_date.isoformat(),
            "sell_trade_date": sell_trade_date.isoformat(),
            "sell_price": sell_price,
            "pnl": pnl,
            "status": "CLOSED"
        }) \
        .eq("id", trade_id) \
        .execute()

    print(f"[✅] SELL trade closed: {symbol} ({buy_type}) @ {sell_price} | PnL = {pnl}")

def get_today_buy_signals(signal_date):
    date1 = str(signal_date)
    response = supabase.table("signals") \
        .select("symbol, type") \
        .eq("date", date1) \
        .in_("type", ["BUY", "LONG_TERM_BUY"]) \
        .execute()

    return response.data if response.data else []

def get_today_sell_signals(signal_date):
    date1 = str(signal_date)
    result = supabase.table("signals") \
        .select("symbol, type") \
        .eq("date", date1) \
        .in_("type",  ["SELL", "LONG_TERM_SELL"]) \
        .execute()
    return result.data if result.data else []

def get_trade_log():
    result = supabase.table("trade_log").select("*").order("buy_trade_date", desc=True).execute()
    return result.data if result.data else []

def getOpentrades():
    open_trades = supabase.table("trade_log") \
        .select("*") \
        .eq("status", "OPEN") \
        .execute().data
    return open_trades.data if open_trades.data else []
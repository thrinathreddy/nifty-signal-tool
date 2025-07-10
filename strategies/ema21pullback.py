import pandas as pd

def generate_signal(df):
    if df is None or len(df) < 2:
        return "HOLD"

    today = df.iloc[-1]
    prev = df.iloc[-2]

    # Today's conditions
    cond_today_up = today["close"] > today["open"]
    cond_today_above_ema = today["close"] > today["ema_21"] and today["open"] > today["ema_21"]

    # Yesterday's EMA21 between yesterday's open and close
    cond_prev_ema_between = (
        min(prev["close"], prev["open"]) < prev["ema_21"] < max(prev["close"], prev["open"])
    )

    if cond_today_up and cond_today_above_ema and cond_prev_ema_between:
        return "BUY"

    return "HOLD"

import pandas as pd

def generate_signal(df, n=20):
    if len(df) < n + 2:
        return "HOLD"

    today = df.iloc[-1]
    yesterday = df.iloc[-2]
    prior_lows = df["low"].iloc[-(n+2):-2]

    min_low = prior_lows.min()

    # Price breaks below previous N-day low and closes back inside
    if yesterday["low"] < min_low and today["close"] > min_low:
        return "BUY"

    # Price breaks above previous N-day high and closes back inside
    prior_highs = df["high"].iloc[-(n+2):-2]
    max_high = prior_highs.max()
    if yesterday["high"] > max_high and today["close"] < max_high:
        return "SELL"

    return "HOLD"
  

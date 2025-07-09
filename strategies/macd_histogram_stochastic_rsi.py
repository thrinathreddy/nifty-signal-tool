import pandas as pd


def generate_signal(df):
    if "macd_hist" not in df.columns or len(df) < 2:
        return "HOLD"

    prev = df.iloc[-2]
    curr = df.iloc[-1]

    k = curr.get("stoch_k")
    d = curr.get("stoch_d")

    if prev["macd_hist"] < 0 and curr["macd_hist"] > 0 and k < 20 and k > d:
        return "BUY"
    elif prev["macd_hist"] > 0 and curr["macd_hist"] < 0:
        return "SELL"

    return "HOLD"
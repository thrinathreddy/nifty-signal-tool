import pandas as pd

def generate_signal(df):
    if len(df) < 31:
        return "HOLD"

    df["ema9"] = df["close"].ewm(span=9, adjust=False).mean()
    df["ema30"] = df["close"].ewm(span=30, adjust=False).mean()

    latest = df.iloc[-1]

    if df["ema9"].iloc[-1] > df["ema30"].iloc[-1] and abs(latest["close"] - df["ema30"].iloc[-1]) / df["ema30"].iloc[-1] < 0.01:
        return "BUY"
    elif df["ema9"].iloc[-1] < df["ema30"].iloc[-1] and abs(latest["close"] - df["ema30"].iloc[-1]) / df["ema30"].iloc[-1] < 0.01:
        return "SELL"
    return "HOLD"

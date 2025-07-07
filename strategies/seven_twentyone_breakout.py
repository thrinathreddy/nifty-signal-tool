import pandas as pd

def generate_signal(df):
    if len(df) < 22:
        return "HOLD"

    df["ema7"] = df["close"].ewm(span=7, adjust=False).mean()
    df["ema21"] = df["close"].ewm(span=21, adjust=False).mean()

    # Check last two values for crossover
    if df["ema7"].iloc[-2] < df["ema21"].iloc[-2] and df["ema7"].iloc[-1] > df["ema21"].iloc[-1]:
        return "BUY"
    elif df["ema7"].iloc[-2] > df["ema21"].iloc[-2] and df["ema7"].iloc[-1] < df["ema21"].iloc[-1]:
        return "SELL"
    return "HOLD"

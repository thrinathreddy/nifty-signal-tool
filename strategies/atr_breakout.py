import pandas as pd
def generate_signal(df):
    if "atr" not in df.columns:
        return "HOLD"
    latest = df.iloc[-1]
    close = latest["close"]
    high = latest["high"]
    low = latest["low"]
    atr = latest["atr"]
    if pd.isna(atr):
        return "HOLD"
    if high > close + atr:
        return "BUY"
    elif low < close - atr:
        return "SELL"
    return "HOLD"
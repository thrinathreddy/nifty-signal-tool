# breakout_volatility.py
import pandas as pd

def generate_signal(df):
    if df is None or len(df) < 21:
        return "HOLD"

    latest = df.iloc[-1]
    prev_high = df["high"].iloc[-21:-1].max()
    atr = df["atr"].iloc[-1]
    atr_prev = df["atr"].iloc[-2] if len(df) >= 22 else atr

    if pd.isna(prev_high) or pd.isna(atr) or pd.isna(atr_prev):
        return "HOLD"

    if latest["close"] > prev_high and atr > atr_prev:
        return "BUY"
    elif latest["close"] < df["low"].iloc[-21:-1].min() and atr > atr_prev:
        return "SELL"
    return "HOLD"

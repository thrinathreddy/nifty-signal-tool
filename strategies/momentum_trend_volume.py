# momentum_trend_volume.py
import pandas as pd

def generate_signal(df):
    if df is None or len(df) < 51:
        return "HOLD"

    latest = df.iloc[-1]
    avg_volume = df["volume"].rolling(20).mean().iloc[-1]

    if pd.isna(latest["rsi"]) or pd.isna(latest["ema50"]) or pd.isna(avg_volume):
        return "HOLD"

    if latest["close"] > latest["ema50"] and latest["rsi"] > 60 and latest["volume"] > avg_volume:
        return "BUY"
    elif latest["close"] < latest["ema50"] and latest["rsi"] < 40 and latest["volume"] > avg_volume:
        return "SELL"
    return "HOLD"

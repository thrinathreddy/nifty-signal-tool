import pandas as pd


def generate_signal(df):
    latest = df.iloc[-1]
    rsi = latest.get("rsi")
    macd = latest.get("macd")
    macd_signal = latest.get("macd_signal")
    if any(pd.isna([rsi, macd, macd_signal])):
        return "HOLD"
    if rsi < 40 and macd > macd_signal:
        return "BUY"
    elif rsi > 60 and macd < macd_signal:
        return "SELL"
    return "HOLD"
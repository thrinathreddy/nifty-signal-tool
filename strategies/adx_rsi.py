import pandas as pd
def generate_signal(df):
    latest = df.iloc[-1]
    adx = latest.get("adx")
    rsi = latest.get("rsi")
    if pd.isna(adx) or pd.isna(rsi):
        return "HOLD"
    if adx > 25 and rsi < 40:
        return "BUY"
    elif adx > 25 and rsi > 60:
        return "SELL"
    return "HOLD"
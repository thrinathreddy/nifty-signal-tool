import pandas as pd
def generate_signal(df):
    latest = df.iloc[-1]
    rsi = latest.get("rsi")
    close = latest["close"]
    ema_21 = latest.get("ema_21")
    if pd.isna(rsi) or pd.isna(ema_21):
        return "HOLD"
    if rsi < 40 and close > ema_21:
        return "BUY"
    elif rsi > 60 and close < ema_21:
        return "SELL"
    return "HOLD"
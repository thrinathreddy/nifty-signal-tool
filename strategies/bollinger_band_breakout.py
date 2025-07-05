import pandas as pd
def generate_signal(df):
    latest = df.iloc[-1]
    close = latest["close"]
    upper = latest.get("bb_upper")
    lower = latest.get("bb_lower")
    if pd.isna(upper) or pd.isna(lower):
        return "HOLD"
    if close > upper:
        return "BUY"
    elif close < lower:
        return "SELL"
    return "HOLD"

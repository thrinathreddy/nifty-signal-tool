import pandas as pd
def generate_signal(df):
    latest = df.iloc[-1]
    k = latest.get("stoch_k")
    d = latest.get("stoch_d")
    if pd.isna(k) or pd.isna(d):
        return "HOLD"
    if k < 20 and k > d:
        return "BUY"
    elif k > 80 and k < d:
        return "SELL"
    return "HOLD"
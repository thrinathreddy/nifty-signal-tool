def generate_signal(df):
    if len(df) < 2 or "supertrend" not in df.columns:
        return "HOLD"
    prev = df.iloc[-2]
    curr = df.iloc[-1]
    if prev["supertrend"] == False and curr["supertrend"] == True:
        return "BUY"
    elif prev["supertrend"] == True and curr["supertrend"] == False:
        return "SELL"
    return "HOLD"

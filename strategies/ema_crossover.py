def generate_signal(df):
    if len(df) < 2 or "ema_20" not in df.columns or "ema_50" not in df.columns:
        return "HOLD"
    prev = df.iloc[-2]
    curr = df.iloc[-1]
    if prev["ema_20"] < prev["ema_50"] and curr["ema_20"] > curr["ema_50"]:
        return "BUY"
    elif prev["ema_20"] > prev["ema_50"] and curr["ema_20"] < curr["ema_50"]:
        return "SELL"
    return "HOLD"
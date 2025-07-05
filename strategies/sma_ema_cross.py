def generate_signal(df):
    if len(df) < 2 or "sma_50" not in df.columns or "ema_21" not in df.columns:
        return "HOLD"
    prev = df.iloc[-2]
    curr = df.iloc[-1]
    if prev["ema_21"] < prev["sma_50"] and curr["ema_21"] > curr["sma_50"]:
        return "BUY"
    elif prev["ema_21"] > prev["sma_50"] and curr["ema_21"] < curr["sma_50"]:
        return "SELL"
    return "HOLD"
def generate_signal(df):
    if "macd_hist" not in df.columns or len(df) < 2:
        return "HOLD"

    prev = df.iloc[-2]
    curr = df.iloc[-1]

    if prev["macd_hist"] < 0 and curr["macd_hist"] > 0:
        return "BUY"
    elif prev["macd_hist"] > 0 and curr["macd_hist"] < 0:
        return "SELL"

    return "HOLD"
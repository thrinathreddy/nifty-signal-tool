import pandas_ta as ta

def apply_indicators(df):
    df["rsi"] = ta.rsi(df["Close"], length=14)
    macd = ta.macd(df["Close"])
    df["macd"] = macd["MACD_12_26_9"]
    df["macd_signal"] = macd["MACDs_12_26_9"]
    df["ema50"] = ta.ema(df["Close"], length=50)
    df["ema200"] = ta.ema(df["Close"], length=200)
    return df

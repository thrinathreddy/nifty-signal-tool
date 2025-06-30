import pandas_ta as ta

def apply_indicators(df):
    if df is None or df.empty or "Close" not in df.columns:
        print("[❌] Invalid or empty DataFrame in apply_indicators")
        return None

    try:
        df["rsi"] = ta.rsi(df["Close"], length=14)

        macd_df = ta.macd(df["Close"])
        if macd_df is not None and not macd_df.empty:
            df["macd"] = macd_df.iloc[:, 0]  # safer than hardcoding column names
            df["macd_signal"] = macd_df.iloc[:, 1]
        else:
            df["macd"] = None
            df["macd_signal"] = None

        df["ema50"] = ta.ema(df["Close"], length=50)
        df["ema200"] = ta.ema(df["Close"], length=200)

    except Exception as e:
        print(f"[‼️] Indicator application failed: {e}")
        return None

    return df
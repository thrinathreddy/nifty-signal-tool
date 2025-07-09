import pandas_ta as ta
import pandas as pd
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def apply_indicators(df):
    if df is None or df.empty or "Close" not in df.columns:
        logger.error("[❌] Invalid or empty DataFrame in apply_indicators")
        return None

    try:
        df["Close"] = pd.to_numeric(df["Close"], errors="coerce")
        df = df.dropna(subset=["Close"])

        if df.empty:
            logger.error("❌ DataFrame is empty after cleaning 'Close' column.")
            return None

        # EMA for 9 and 30
        logger.info("📉 Calculating EMA9 and EMA30...")
        df["ema9"] = ta.ema(df["Close"], length=9)
        df["ema30"] = ta.ema(df["Close"], length=30)

        # 20-day High/Low for Turtle Soup
        logger.info("📈 Calculating 20-day high/low for Turtle Soup...")
        df["20d_low"] = df["Low"].rolling(window=20).min()
        df["20d_high"] = df["High"].rolling(window=20).max()

    except Exception as e:
        logger.exception(f"[‼️] Indicator application failed: {e}")
        return None

    logger.info("✅ Indicators successfully applied.")
    return df

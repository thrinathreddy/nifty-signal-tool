# indicators.py
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
        # Ensure Close column is numeric
        df["Close"] = pd.to_numeric(df["Close"], errors="coerce")
        nan_count = df["Close"].isna().sum()
        if nan_count > 0:
            logger.warning(f"⚠️ Found {nan_count} NaNs in 'Close' column. Dropping them.")
            df = df.dropna(subset=["Close"])

        logger.info(f"📄 DataFrame length after cleaning: {len(df)} rows")
        logger.debug(df.tail(5).to_string())

        logger.info("🧮 Calculating RSI...")
        df["rsi"] = ta.rsi(df["Close"], length=14)

        logger.info("📈 Calculating MACD...")
        if len(df) >= 50:
            macd_df = ta.macd(df["Close"])
            if macd_df is not None and not macd_df.empty:
                df["macd"] = macd_df.iloc[:, 0]
                df["macd_signal"] = macd_df.iloc[:, 1]
                logger.info("✅ MACD and Signal added.")
            else:
                df["macd"] = None
                df["macd_signal"] = None
                logger.warning("⚠️ MACD calculation returned empty DataFrame.")
        else:
            df["macd"] = None
            df["macd_signal"] = None
            logger.warning("⚠️ Not enough data (min 50 rows) for MACD calculation.")

        logger.info("📉 Calculating EMA50 and EMA200...")
        df["ema50"] = ta.ema(df["Close"], length=50)
        df["ema200"] = ta.ema(df["Close"], length=200)

    except Exception as e:
        logger.exception(f"[‼️] Indicator application failed: {e}")
        return None

    logger.info("✅ Indicators successfully applied.")
    return df

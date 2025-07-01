# indicators.py
import pandas_ta as ta
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def apply_indicators(df):
    if df is None or df.empty or "Close" not in df.columns:
        logger.error("[❌] Invalid or empty DataFrame in apply_indicators")
        return None

    try:
        logger.info("🧮 Calculating RSI...")
        df["rsi"] = ta.rsi(df["Close"], length=14)

        logger.info("📈 Calculating MACD...")
        logger.info(f"📄 DataFrame length: {len(df)} rows")
        logger.debug(df.tail(5).to_string())
        macd_df = ta.macd(df["Close"])
        if macd_df is not None and not macd_df.empty:
            df["macd"] = macd_df.iloc[:, 0]
            df["macd_signal"] = macd_df.iloc[:, 1]
            logger.info("✅ MACD and Signal added.")
        else:
            df["macd"] = None
            df["macd_signal"] = None
            logger.warning("⚠️ MACD calculation returned empty DataFrame.")

        logger.info("📉 Calculating EMA50 and EMA200...")
        df["ema50"] = ta.ema(df["Close"], length=50)
        df["ema200"] = ta.ema(df["Close"], length=200)

    except Exception as e:
        logger.exception(f"[‼️] Indicator application failed: {e}")
        return None

    logger.info("✅ Indicators successfully applied.")
    return df

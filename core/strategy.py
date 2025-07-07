# strategy.py
import pandas as pd
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def generate_signal(df):
    if df is None or df.empty:
        logger.error("❌ Empty or None DataFrame received in generate_signal.")
        return "HOLD"

    latest = df.iloc[-1]
    prev = df.iloc[-2] if len(df) >= 2 else latest

    try:
        # Ensure required indicators are present
        required = ["Close", "Low", "High", "ema9", "ema30", "20d_low", "20d_high"]
        if any(pd.isna(latest.get(col)) for col in required):
            logger.warning("⚠️ Missing indicator data, returning HOLD.")
            return "HOLD"

        close = latest["Close"]
        ema9 = latest["ema9"]
        ema30 = latest["ema30"]
        low = latest["Low"]
        high = latest["High"]
        low20 = latest["20d_low"]
        high20 = latest["20d_high"]

        # --- 9-30 Pullback Buy ---
        near_ema30 = abs(close - ema30) / ema30 < 0.01  # within 1%
        if ema9 > ema30 and close < ema9 and near_ema30 and low < low20 and close > low20:
            logger.info("✅ BUY from 9-30 + Turtle Soup confluence.")
            return "BUY"
        # --- Turtle Soup Sell ---
        if high > high20 and close < high20:
            logger.info("✅ SELL from Turtle Soup false breakout reversal.")
            return "SELL"

    except Exception as e:
        logger.exception(f"❌ Error in generate_signal: {e}")

    logger.info("ℹ️ HOLD signal (no trigger from combined strategy).")
    return "HOLD"


# strategy.py
import pandas as pd
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def generate_signal(df):
    if df is None or df.empty:
        logger.error("❌ Empty or None DataFrame received in generate_signal.")
        return None

    latest = df.iloc[-1]

    # Check for NaNs
    required_columns = ["rsi", "macd", "macd_signal"]
    missing = [col for col in required_columns if col not in latest or pd.isna(latest[col])]

    if missing:
        logger.warning(f"⚠️ Cannot generate signal — missing/NaN values in: {missing}")
        return "HOLD"

    rsi = latest["rsi"]
    macd = latest["macd"]
    macd_signal = latest["macd_signal"]

    logger.info(f"📊 Latest indicators — RSI: {rsi:.2f}, MACD: {macd:.2f}, Signal: {macd_signal:.2f}")

    if rsi < 30 and macd > macd_signal:
        logger.info("✅ BUY signal generated.")
        return "BUY"
    elif rsi > 70 and macd < macd_signal:
        logger.info("✅ SELL signal generated.")
        return "SELL"
    
    logger.info("ℹ️ HOLD signal (no action).")
    return "HOLD"

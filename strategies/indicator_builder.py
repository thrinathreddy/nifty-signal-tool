import ta
import yfinance as yf
import pandas as pd
from strategies.strategy_registry import STRATEGY_MAP

import logging
logging.basicConfig(level=logging.INFO)
MIN_AVG_VOLUME = 100000

def prepare_indicators(df, strategy_name):
    if df is None or df.empty or len(df) < 20:
        return df  # Not enough data, return as is
    df = df.copy()

    # Basic indicators used across many strategies
    if "rsi" not in df.columns:
        df["rsi"] = ta.momentum.RSIIndicator(df["close"]).rsi()

    if "macd" not in df.columns or "macd_signal" not in df.columns:
        macd = ta.trend.MACD(df["close"])
        df["macd"] = macd.macd()
        df["macd_signal"] = macd.macd_signal()
        df["macd_hist"] = macd.macd_diff()

    if "ema_20" not in df.columns:
        df["ema_20"] = ta.trend.EMAIndicator(df["close"], window=20).ema_indicator()
    if "ema_50" not in df.columns:
        df["ema_50"] = ta.trend.EMAIndicator(df["close"], window=50).ema_indicator()
    if "ema_21" not in df.columns:
        df["ema_21"] = ta.trend.EMAIndicator(df["close"], window=21).ema_indicator()

    if "sma_50" not in df.columns:
        df["sma_50"] = ta.trend.SMAIndicator(df["close"], window=50).sma_indicator()

    if strategy_name == "Bollinger Band Breakout":
        bb = ta.volatility.BollingerBands(df["close"])
        df["bb_upper"] = bb.bollinger_hband()
        df["bb_lower"] = bb.bollinger_lband()

    if strategy_name == "Stochastic RSI":
        stoch = ta.momentum.StochRSIIndicator(df["close"])
        df["stoch_k"] = stoch.stochrsi_k()
        df["stoch_d"] = stoch.stochrsi_d()

    if strategy_name == "ADX + RSI":
        df["adx"] = ta.trend.ADXIndicator(df["high"], df["low"], df["close"]).adx()

    if strategy_name == "Supertrend":
        st = ta.volatility.AverageTrueRange(df["high"], df["low"], df["close"])
        df["atr"] = st.average_true_range()
        df["supertrend"] = df["close"] > (df["close"] - df["atr"])  # dummy logic, replace if you have real one

    if strategy_name == "ATR Breakout":
        df["atr"] = ta.volatility.AverageTrueRange(df["high"], df["low"], df["close"]).average_true_range()

    return df

def run_backtest(symbol, strategy_name, period, share_count=1, stop_loss_pct=5.0, target_pct=10.0):
    data = yf.download(symbol + ".NS", period=period, interval="1d", auto_adjust=True, progress=False)
    if len(data) < 2:
        return []

    data.columns = data.columns.get_level_values(0)
    if data["Volume"].mean() < MIN_AVG_VOLUME:
        print(f"⚠️ Skipping {symbol} due to low avg volume: {data['Volume'].mean():,.0f}")
        return []

    data = data.rename(columns={
        "Open": "open", "High": "high", "Low": "low",
        "Close": "close", "Volume": "volume"
    })
    data = prepare_indicators(data, strategy_name)

    trades = []
    position = None
    buy_price = 0

    BROKERAGE_RATE = 0.0003  # 0.03%
    GST_RATE = 0.18  # 18% GST on brokerage

    for i in range(len(data)):
        sub_df = data.iloc[:i + 1]
        today = sub_df.iloc[-1]
        close = today["close"]

        if position == "LONG":
            pct_change = (close - buy_price) / buy_price * 100
            if pct_change >= target_pct or pct_change <= -stop_loss_pct:
                turnover = (buy_price + close) * share_count
                brokerage = turnover * BROKERAGE_RATE
                gst = brokerage * GST_RATE
                gross_pnl = (close - buy_price) * share_count
                net_pnl = round(gross_pnl - brokerage - gst, 2)

                trades[-1] = (
                    sub_df.index[-1], "EXIT", buy_price, close,
                    round(gross_pnl, 2), round(brokerage, 2),
                    round(gst, 2), net_pnl
                )
                position = None
                continue

        signal = STRATEGY_MAP[strategy_name].generate_signal(sub_df)
        if signal == "BUY" and position is None:
            buy_price = close
            position = "LONG"
            trades.append((sub_df.index[-1], signal, buy_price, None, None, None, None, None))

        elif signal == "SELL" and position == "LONG":
            turnover = (buy_price + close) * share_count
            brokerage = turnover * BROKERAGE_RATE
            gst = brokerage * GST_RATE
            gross_pnl = (close - buy_price) * share_count
            net_pnl = round(gross_pnl - brokerage - gst, 2)

            trades[-1] = (
                sub_df.index[-1], signal, buy_price, close,
                round(gross_pnl, 2), round(brokerage, 2),
                round(gst, 2), net_pnl
            )
            position = None

    return [t for t in trades if t[-1] is not None]

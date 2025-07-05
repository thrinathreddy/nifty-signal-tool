import ta
import yfinance as yf
import pandas as pd
from strategies.strategy_registry import STRATEGY_MAP

from core.backtester import backtest


def prepare_indicators(df, strategy_name):
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

def run_backtest(symbol, strategy_name, period):
    data = yf.download(symbol, period=period, interval="1d", auto_adjust=True, progress=False)
    data.columns = data.columns.get_level_values(0)
    data = data.rename(columns={"Open": "open", "High": "high", "Low": "low", "Close": "close", "Volume": "volume"})

    data = prepare_indicators(data, strategy_name)
    signals = []
    position = None
    buy_price = 0
    for i in range(len(data)):
        sub_df = data.iloc[:i + 1]
        signal = STRATEGY_MAP[strategy_name].generate_signal(sub_df)
        if signal == "BUY" and position is None:
            buy_price = sub_df.iloc[-1]["close"]
            position = "LONG"
            signals.append((sub_df.index[-1], signal, buy_price, None))
        elif signal == "SELL" and position == "LONG":
            sell_price = sub_df.iloc[-1]["close"]
            pnl = sell_price - buy_price
            signals[-1] = (*signals[-1][:3], sell_price)
            position = None

    trades = [s for s in signals if s[-1] is not None]
    return trades


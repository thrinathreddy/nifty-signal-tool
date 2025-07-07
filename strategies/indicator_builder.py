import ta
import yfinance as yf
import pandas as pd
from strategies.strategy_registry import STRATEGY_MAP

import logging
logging.basicConfig(level=logging.INFO)
MIN_AVG_VOLUME = 100000


def load_symbol_data(symbol, period="6mo"):
    data = yf.download(symbol + ".NS", period=period, interval="1d", auto_adjust=True, progress=False)

    if len(data) < 2:
        return None

    data.columns = data.columns.get_level_values(0)

    if data["Volume"].mean() < MIN_AVG_VOLUME:
        print(f"⚠️ Skipping {symbol} due to low avg volume: {data['Volume'].mean():,.0f}")
        return None

    return data.rename(columns={
        "Open": "open", "High": "high", "Low": "low",
        "Close": "close", "Volume": "volume"
    })

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

def run_backtest(symbol, strategy_name, data, share_count=1, stop_loss_pct=5.0, target_pct=10.0):
    if data is  None:
        return None
    data = prepare_indicators(data, strategy_name)

    trades = []
    position = None
    buy_price = 0

    BROKERAGE_RATE = 0.0003  # 0.03%
    GST_RATE = 0.18  # 18% GST on brokerage
    STT_RATE = 0.001  # 0.1% STT on sell side (for delivery)

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
                stt = close * share_count * STT_RATE
                exchange_txn = turnover * EXCHANGE_TXN_RATE
                sebi_fee = turnover * SEBI_FEE_RATE
                stamp_duty = buy_price * share_count * STAMP_DUTY_RATE
                gross_pnl = (close - buy_price) * share_count
                net_pnl = round(gross_pnl - brokerage - gst - stt - exchange_txn - sebi_fee - stamp_duty, 2)

                trades[-1] = (
                    sub_df.index[-1], "EXIT", buy_price, close,
                    round(gross_pnl, 2), round(brokerage, 2),
                    round(gst, 2), round(stt, 2), round(exchange_txn + sebi_fee + stamp_duty, 2), net_pnl
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
            stt = close * share_count * STT_RATE
            exchange_txn = turnover * EXCHANGE_TXN_RATE
            sebi_fee = turnover * SEBI_FEE_RATE
            stamp_duty = buy_price * share_count * STAMP_DUTY_RATE
            gross_pnl = (close - buy_price) * share_count
            net_pnl = round(gross_pnl - brokerage - gst - stt - exchange_txn - sebi_fee - stamp_duty, 2)

            trades[-1] = (
                sub_df.index[-1], signal, buy_price, close,
                round(gross_pnl, 2), round(brokerage, 2),
                round(gst, 2), round(stt, 2), round(exchange_txn + sebi_fee + stamp_duty, 2), net_pnl
            )
            position = None

    return [t for t in trades if t[-1] is not None]

def run_all_backtests(symbol, period="6mo", share_count=1, stop_loss_pct=5.0, target_pct=10.0):
    summary = []
    data = load_symbol_data(symbol, period)
    if data is not None:
        for strategy_name in STRATEGY_MAP.keys():
            working_data = data.copy()
            trades = run_backtest(symbol, strategy_name, working_data, share_count, stop_loss_pct, target_pct)
            if trades:
                df = pd.DataFrame(trades, columns=["Date", "Signal", "Buy", "Sell", "Gross PnL", "Brokerage", "GST", "Net PnL"])
                df["Date"] = pd.to_datetime(df["Date"])
                df["ExitDate"] = df["Date"].shift(-1).fillna(df["Date"].iloc[-1])
                df["Duration"] = (df["ExitDate"] - df["Date"]).dt.days
                df["Cumulative Net PnL"] = df["Net PnL"].cumsum()

                sharpe = round(df["Net PnL"].mean() / df["Net PnL"].std(), 2) if df["Net PnL"].std() > 0 else 0
                win_ratio = round((df["Net PnL"] > 0).mean() * 100, 2)
                total_net_pnl = round(df["Net PnL"].sum(), 2)
                avg_duration = round(df["Duration"].mean(), 2)
                max_drawdown = round((df["Cumulative Net PnL"] - df["Cumulative Net PnL"].cummax()).min(), 2)

                summary.append({
                    "Strategy": strategy_name,
                    "Trades": len(df),
                    "Wins (%)": win_ratio,
                    "Net PnL": total_net_pnl,
                    "Avg Duration": avg_duration,
                    "Sharpe": sharpe,
                    "Max Drawdown": max_drawdown,
                })

        return pd.DataFrame(summary).sort_values(by="Net PnL", ascending=False).reset_index(drop=True)
    return None

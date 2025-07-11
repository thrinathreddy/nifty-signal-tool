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

    # RSI
    if "rsi" not in df.columns:
        df["rsi"] = ta.momentum.RSIIndicator(df["close"]).rsi()

    # MACD
    if "macd" not in df.columns or "macd_signal" not in df.columns:
        macd = ta.trend.MACD(df["close"])
        df["macd"] = macd.macd()
        df["macd_signal"] = macd.macd_signal()
        df["macd_hist"] = macd.macd_diff()

    # EMAs and SMAs
    if "ema_20" not in df.columns:
        df["ema_20"] = ta.trend.EMAIndicator(df["close"], window=20).ema_indicator()
    if "ema_21" not in df.columns:
        df["ema_21"] = ta.trend.EMAIndicator(df["close"], window=21).ema_indicator()
    if "ema_50" not in df.columns:
        df["ema_50"] = ta.trend.EMAIndicator(df["close"], window=50).ema_indicator()
    if "sma_50" not in df.columns:
        df["sma_50"] = ta.trend.SMAIndicator(df["close"], window=50).sma_indicator()

    # ATR
    if "atr" not in df.columns:
        df["atr"] = ta.volatility.AverageTrueRange(df["high"], df["low"], df["close"]).average_true_range()

    # Volume average for momentum + volume strategy
    if "vol_avg_20" not in df.columns:
        df["vol_avg_20"] = df["volume"].rolling(window=20).mean()

    # Rolling highs/lows for TurtleSoup & Breakout
    if "high_20" not in df.columns:
        df["high_20"] = df["high"].rolling(window=20).max()
    if "low_20" not in df.columns:
        df["low_20"] = df["low"].rolling(window=20).min()

    # Strategy-specific indicators
    if strategy_name == "Bollinger Band Breakout":
        bb = ta.volatility.BollingerBands(df["close"])
        df["bb_upper"] = bb.bollinger_hband()
        df["bb_lower"] = bb.bollinger_lband()

    if strategy_name == "Stochastic RSI" or strategy_name == "MACD Histogram with Stochastic RSI":
        stoch = ta.momentum.StochRSIIndicator(df["close"])
        df["stoch_k"] = stoch.stochrsi_k()
        df["stoch_d"] = stoch.stochrsi_d()

    if strategy_name == "ADX + RSI":
        df["adx"] = ta.trend.ADXIndicator(df["high"], df["low"], df["close"]).adx()

    if strategy_name == "Supertrend":
        st = ta.volatility.AverageTrueRange(df["high"], df["low"], df["close"])
        df["atr"] = st.average_true_range()
        df["supertrend"] = df["close"] > (df["close"] - df["atr"])  # dummy logic

    return df
    
def run_backtest(symbol, strategy_name, data, share_count=1, stop_loss_pct=5.0, target_pct=10.0):
    if data is None or len(data) < 2:
        return None

    data = prepare_indicators(data, strategy_name)
    trades = []
    position = None
    buy_price = 0
    peak_price = 0

    # Charges
    BROKERAGE_RATE = 0.0003
    GST_RATE = 0.18
    STT_RATE = 0.001
    EXCHANGE_TXN_RATE = 0.0000345
    SEBI_FEE_RATE = 0.000001
    STAMP_DUTY_RATE = 0.00015

    for i in range(len(data) - 1):  # leave room for next day's open
        today = data.iloc[i]
        next_day = data.iloc[i + 1]
        sub_df = data.iloc[:i + 1]

        # Check exit conditions
        if position == "LONG":
            open_price = today["open"]
            high = today["high"]
            low = today["low"]

            # Update peak price for trailing stop
            peak_price = max(peak_price, high)

            target_price = buy_price * (1 + target_pct / 100)
            stop_price = buy_price * (1 - stop_loss_pct / 100)

            sell_price = None
            reason = None

            # --- Priority 1: Check if stop-loss or target hit on market open ---
            if open_price <= stop_price:
                sell_price = open_price
                reason = "STOPLOSS (Gap)"
            elif open_price >= target_price:
                sell_price = open_price
                reason = "TARGET (Gap)"

            # --- Priority 2: Normal intraday range checks ---
            elif high >= target_price:
                sell_price = target_price
                reason = "TARGET"
            elif low <= stop_price:
                sell_price = stop_price
                reason = "STOPLOSS"

            if sell_price is not None:
                turnover = (buy_price + sell_price) * share_count
                brokerage = turnover * BROKERAGE_RATE
                gst = brokerage * GST_RATE
                stt = sell_price * share_count * STT_RATE
                exchange_txn = turnover * EXCHANGE_TXN_RATE
                sebi_fee = turnover * SEBI_FEE_RATE
                stamp_duty = buy_price * share_count * STAMP_DUTY_RATE
                gross_pnl = (sell_price - buy_price) * share_count
                net_pnl = round(gross_pnl - brokerage - gst - stt - exchange_txn - sebi_fee - stamp_duty, 2)

                entry = trades[-1]
                trades[-1] = (
                    entry[0],  # original buy date
                    reason,
                    buy_price,
                    sell_price,
                    round(gross_pnl, 2),
                    round(brokerage, 2),
                    round(gst, 2),
                    round(stt, 2),
                    round(exchange_txn + sebi_fee + stamp_duty, 2),
                    net_pnl,
                    today.name,  # actual exit date
                    reason
                )
                position = None
                peak_price = 0
                continue

        # Entry Signal
        signal = STRATEGY_MAP[strategy_name].generate_signal(sub_df)

        if signal == "BUY" and position is None:
            print("buy placing")

            print(today.name)
            print(next_day.name)
            buy_price = next_day["open"]  # buy on next day open
            print(buy_price)
            peak_price = buy_price
            position = "LONG"
            trades.append((
                next_day.name, signal, buy_price, None, None, None, None, None, None, None, None
            ))
        elif signal == "SELL" and position == "LONG":
            sell_price = today["close"]
            turnover = (buy_price + sell_price) * share_count
            brokerage = turnover * BROKERAGE_RATE
            gst = brokerage * GST_RATE
            stt = sell_price * share_count * STT_RATE
            exchange_txn = turnover * EXCHANGE_TXN_RATE
            sebi_fee = turnover * SEBI_FEE_RATE
            stamp_duty = buy_price * share_count * STAMP_DUTY_RATE
            gross_pnl = (sell_price - buy_price) * share_count
            net_pnl = round(gross_pnl - brokerage - gst - stt - exchange_txn - sebi_fee - stamp_duty, 2)

            trades[-1] = (
                today.name, signal, buy_price, sell_price,
                round(gross_pnl, 2), round(brokerage, 2),
                round(gst, 2), round(stt, 2),
                round(exchange_txn + sebi_fee + stamp_duty, 2),
                net_pnl
            )
            position = None
            peak_price = 0
    print(trades)
    return [t for t in trades if t[-1] is not None]

def run_all_backtests(symbol, period="6mo", share_count=1, stop_loss_pct=5.0, target_pct=10.0):
    summary = []
    data = load_symbol_data(symbol, period)
    if data is not None:
        for strategy_name in STRATEGY_MAP.keys():
            working_data = data.copy()
            trades = run_backtest(symbol, strategy_name, working_data, share_count, stop_loss_pct, target_pct)
            if trades:
                df = pd.DataFrame(trades, columns=["Date", "Signal", "Buy", "Sell", "Gross PnL", "Brokerage", "GST", "STT", "Other Chrgs", "Net PnL", "ExitDate", "Reason"])
                df["Date"] = pd.to_datetime(df["Date"])
                df["ExitDate"] = pd.to_datetime(df["ExitDate"])
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

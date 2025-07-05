import streamlit as st
import os
import sys
from datetime import datetime, timedelta, date
import pandas as pd
import altair as alt
import numpy as np

# Add project root to sys.path to fix imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from run_daily import run_scan
from run_daily2 import run_scan2
from core.db_handler import get_signals, get_trade_log
from strategies.indicator_builder import run_backtest
from strategies.strategy_registry import STRATEGY_MAP
from strategies.stockSymbols import STOCKS

# Streamlit UI config
st.set_page_config(page_title="Nifty50 Signal Dashboard", layout="centered")

# App title
st.title("📈 Nifty50 Signal Dashboard")
st.markdown("""
Welcome to your custom stock signal scanner tool!  
This dashboard shows:
- **Short-term technical BUY signals**
- **Long-term investment picks** based on fundamentals
""")

# Run scanner manually
if st.button("🔁 Run Scanner"):
    with st.spinner("Running scan on all Nifty50 stocks..."):
        run_scan()
    st.success("✅ Scan completed successfully!")

# Query params for automation
query_params = st.query_params
if "scan" in query_params and query_params["scan"].lower() == "yes":
    with st.spinner("🔄 Scan triggered from URL..."):
        run_scan()
    st.success("✅ Scan completed via URL trigger!")

if "logTrades" in query_params and query_params["logTrades"].lower() == "yes":
    run_scan2()

# Load all signals and trade logs
signals = get_signals() or []
trade_log = get_trade_log() or []

# Helper: format date
def format_date(date_str):
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").strftime("%b %d, %Y")
    except Exception:
        return date_str

# Create tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "📅 Short-Term Signals",
    "🏦 Long-Term Investment Picks",
    "📘 Trade Log & Performance",
    "🧪 Backtest Strategies"
])

# --- TAB 1: SHORT TERM SIGNALS ---
with tab1:
    st.subheader("📅 Short-Term Signals")

    signals = get_signals() or []

    last_7_days = [date.today() - timedelta(days=i) for i in range(7)]
    last_7_days_str = [d.strftime("%Y-%m-%d") for d in reversed(last_7_days)]
    selected_date = st.selectbox("📅 Select Signal Date", last_7_days_str, index=6, key="short_term_date")

    filtered_signals = [s for s in signals if s.get("date") == selected_date]
    short_term = [s for s in filtered_signals if s.get("type") == "BUY"]

    st.subheader(f"Technical BUY Signals on {format_date(selected_date)}")
    if short_term:
        st.success(f"📊 {len(short_term)} short-term signals")
        for signal in short_term:
            st.markdown(
                f"✅ **{signal['symbol']}** — 📰 *{str(signal.get('market_sentiment') or '').capitalize()} sentiment*")
    else:
        st.info("No short-term signals for this day.")

# --- TAB 2: LONG TERM SIGNALS ---
with tab2:
    st.subheader("🏦 Long-Term Investment Picks")

    signals = get_signals() or []

    last_7_days = [date.today() - timedelta(days=i) for i in range(7)]
    last_7_days_str = [d.strftime("%Y-%m-%d") for d in reversed(last_7_days)]
    selected_date = st.selectbox("📅 Select Signal Date", last_7_days_str, index=6, key="long_term_date")

    filtered_signals = [s for s in signals if s.get("date") == selected_date]
    long_term = [s for s in filtered_signals if s.get("type") == "LONG_TERM_BUY"]

    st.subheader(f"Long-Term Picks on {format_date(selected_date)}")
    if long_term:
        st.success(f"🏆 {len(long_term)} fundamentally strong picks")
        for signal in long_term:
            st.markdown(f"✅ **{signal['symbol']}** — 📰 *{str(signal.get('market_sentiment') or '').capitalize()} sentiment*")
    else:
        st.info("No long-term picks for this day.")

# --- TAB 3: TRADE LOG & PnL ---
with tab3:
    st.subheader("📘 Trade Log & Performance Summary")

    trade_log = get_trade_log() or []
    open_trades = [t for t in trade_log if t["status"] == "OPEN"]
    closed_trades = [t for t in trade_log if t["status"] == "CLOSED"]
    total_pnl = round(sum(float(t.get("pnl", 0)) for t in closed_trades), 2)

    col1, col2, col3 = st.columns(3)
    col1.metric("📂 Total Trades", len(trade_log))
    col2.metric("🔓 Open Trades", len(open_trades))
    col3.metric("💰 Closed PnL", f"{total_pnl:+.2f}")

    if trade_log:
        df = pd.DataFrame(trade_log)
        df["buy_trade_date"] = pd.to_datetime(df["buy_trade_date"])
        df["sell_trade_date"] = pd.to_datetime(df["sell_trade_date"], errors="coerce")
        df["pnl"] = pd.to_numeric(df["pnl"], errors="coerce").fillna(0)

        # 📈 Cumulative PnL chart
        df_closed = df[df["status"] == "CLOSED"].sort_values("sell_trade_date")
        df_closed["cumulative_pnl"] = df_closed["pnl"].cumsum()

        st.markdown("### 📈 Cumulative PnL Over Time")
        chart = alt.Chart(df_closed).mark_line(point=True).encode(
            x=alt.X("sell_trade_date:T", title="Sell Date"),
            y=alt.Y("cumulative_pnl:Q", title="Cumulative PnL"),
            tooltip=["symbol", "sell_price", "pnl", "cumulative_pnl"]
        ).properties(width=700, height=300)

        st.altair_chart(chart, use_container_width=True)

        # 📊 Profit vs Loss
        st.markdown("### 📊 Profit vs Loss Distribution")
        df_closed["result"] = df_closed["pnl"].apply(lambda x: "Profit" if x > 0 else "Loss")
        dist_chart = alt.Chart(df_closed).mark_bar().encode(
            x=alt.X("result:N", title="Result"),
            y=alt.Y("count():Q", title="Number of Trades"),
            color="result:N"
        ).properties(width=300)

        st.altair_chart(dist_chart, use_container_width=False)

        # 📆 Trades per month
        st.markdown("### 📅 Trade Frequency by Month")
        df_closed["month"] = df_closed["buy_trade_date"].dt.to_period("M").astype(str)
        month_chart = alt.Chart(df_closed).mark_bar().encode(
            x=alt.X("month:N", title="Month"),
            y=alt.Y("count():Q", title="Trades"),
            color=alt.Color("month:N", legend=None)
        ).properties(width=700)

        st.altair_chart(month_chart, use_container_width=True)

        # 📋 Trade Table
        st.markdown("### 📋 Trade Table")
        st.dataframe(
            df[[ "symbol", "buy_type", "buy_trade_date", "buy_price",
                 "sell_trade_date", "sell_price", "pnl", "status" ]].sort_values(by="buy_trade_date", ascending=False),
            use_container_width=True,
        )
    else:
        st.info("No trades logged yet.")


with tab4:
    st.subheader("📊 Backtest Strategy")

    with st.form("backtest_form"):
        strategy = st.selectbox("Select Strategy", list(STRATEGY_MAP.keys()), key="strategy")

        sorted_stock_items = sorted(STOCKS.items(), key=lambda x: x[0])
        stock_display_list = [f"{name} ({symbol})" for name, symbol in sorted_stock_items]
        name_symbol_map = {f"{name} ({symbol})": symbol for name, symbol in sorted_stock_items}

        selected_display = st.selectbox("🔍 Select Stock", stock_display_list, key="stock")
        selected_symbol = name_symbol_map[selected_display]

        period = st.selectbox("Data Period", ["3mo", "6mo", "1y", "2y"], index=2, key="period")
        share_count = st.number_input("🔢 Share Count per Trade", value=1, min_value=1, step=1, key="shares")
        stop_loss = st.number_input("🔒 Stop Loss %", value=5.0, min_value=0.0, key="sl")
        target = st.number_input("🎯 Target %", value=10.0, min_value=0.0, key="target")

        submitted = st.form_submit_button("Run Backtest")

    if submitted:
        trades = run_backtest(selected_symbol, strategy, period, share_count, stop_loss, target)
        if trades:
            df_bt = pd.DataFrame(trades, columns=[
                "Date", "Signal", "Buy", "Sell",
                "Gross PnL", "Brokerage", "GST", "Net PnL"
            ])
            df_bt["Date"] = pd.to_datetime(df_bt["Date"])
            df_bt["Cumulative Net PnL"] = df_bt["Net PnL"].cumsum()
            df_bt["ExitDate"] = df_bt["Date"].shift(-1).fillna(df_bt["Date"].iloc[-1])
            df_bt["Duration"] = (df_bt["ExitDate"] - df_bt["Date"]).dt.days

            total_trades = len(df_bt)
            wins = df_bt[df_bt["Net PnL"] > 0]
            win_ratio = round((len(wins) / total_trades) * 100, 2) if total_trades > 0 else 0
            total_net_pnl = round(df_bt["Net PnL"].sum(), 2)
            avg_duration = round(df_bt["Duration"].mean(), 2)
            running_max = df_bt["Cumulative Net PnL"].cummax()
            drawdown = df_bt["Cumulative Net PnL"] - running_max
            max_drawdown = round(drawdown.min(), 2)
            sharpe_ratio = round(df_bt["Net PnL"].mean() / df_bt["Net PnL"].std(), 2) if df_bt["Net PnL"].std() > 0 else 0

            st.markdown("### 📋 Backtest Summary")
            col1, col2, col3 = st.columns(3)
            col1.metric("📊 Total Trades", total_trades)
            col2.metric("✅ Win Ratio", f"{win_ratio}%")
            col3.metric("💰 Net PnL (₹)", f"{total_net_pnl:+.2f}")

            col4, col5, col6 = st.columns(3)
            col4.metric("⏱ Avg Duration", f"{avg_duration} days")
            col5.metric("📉 Max Drawdown", f"{max_drawdown}")
            col6.metric("📈 Sharpe Ratio", f"{sharpe_ratio}")

            st.markdown("### 📈 Cumulative Net PnL Over Time")
            chart = alt.Chart(df_bt).mark_line(point=True).encode(
                x="Date:T",
                y="Cumulative Net PnL:Q",
                tooltip=["Date", "Buy", "Sell", "Gross PnL", "Net PnL", "Cumulative Net PnL"]
            ).properties(width=700, title=f"Backtest – {selected_symbol.upper()} | Strategy: {strategy}")
            st.altair_chart(chart, use_container_width=True)

            st.markdown("### 🧾 Trade Details")
            st.dataframe(df_bt[[
                "Date", "Buy", "Sell", "Gross PnL",
                "Brokerage", "GST", "Net PnL", "Cumulative Net PnL", "Duration"
            ]])
        else:
            st.warning("⚠️ No trades were executed for this strategy in the selected period.")

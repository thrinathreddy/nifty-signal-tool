import streamlit as st
import os
import sys
from datetime import datetime
import pandas as pd
import altair as alt

# Add project root to sys.path to fix imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from run_daily import run_scan
from run_daily2 import run_scan2
from core.db_handler import get_signals, get_trade_log

# Streamlit UI config
st.set_page_config(page_title="Nifty50 Signal Dashboard", layout="centered")

# App title and intro
st.title("📈 Nifty50 Signal Dashboard")
st.markdown(
    """
    Welcome to your custom stock signal scanner tool!  
    This dashboard shows:
    - **Short-term technical BUY signals**
    - **Long-term investment picks** based on fundamentals
    """
)

# Button to trigger scan manually
if st.button("🔁 Run Scanner"):
    with st.spinner("Running scan on all Nifty50 stocks..."):
        run_scan()
    st.success("✅ Scan completed successfully!")

# 🔍 URL query parameter support (?scan=yes)
query_params = st.query_params
if "scan" in query_params and query_params["scan"].lower() == "yes":
    with st.spinner("🔄 Scan triggered from URL..."):
        run_scan()
    st.success("✅ Scan completed via URL trigger!")
if "logTrades" in query_params and query_params["logTrades"].lower() == "yes":
    run_scan2()

# Load signals from database
signals = get_signals() or []

# Format helper
def format_date(date_str):
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").strftime("%b %d, %Y")
    except Exception:
        return date_str  # fallback

# Separate signals
short_term = [s for s in signals if s.get("type") == "BUY"]
long_term = [s for s in signals if s.get("type") == "LONG_TERM_BUY"]

trade_log = get_trade_log() or []

# Separate open and closed trades
open_trades = [t for t in trade_log if t["status"] == "OPEN"]
closed_trades = [t for t in trade_log if t["status"] == "CLOSED"]

# Calculate total PnL for closed trades
total_pnl = round(sum(float(t.get("pnl", 0)) for t in closed_trades), 2)

# Create tabs for display
tab1, tab2, tab3 = st.tabs([
    "📅 Short-Term Signals",
    "🏦 Long-Term Investment Picks",
    "📘 Trade Log & Performance"
])

# --- TAB 1: SHORT TERM SIGNALS ---
with tab1:
    st.subheader("Today's Technical BUY Signals")
    if short_term:
        st.success(f"📊 {len(short_term)} short-term opportunities found.")
        for signal in short_term:
            st.markdown(f"🔹 **{signal['symbol']}** — `{format_date(signal['date'])}`")
    else:
        st.info("No short-term signals available yet. Run the scanner to generate signals.")

# --- TAB 2: LONG TERM SIGNALS ---
with tab2:
    st.subheader("Long-Term Investment Picks")
    if long_term:
        st.success(f"🏆 {len(long_term)} fundamentally strong stocks identified.")
        for signal in long_term:
            st.markdown(f"✅ **{signal['symbol']}** — `{format_date(signal['date'])}`")
    else:
        st.info("No long-term picks available yet. Try rerunning the fundamental analyzer.")

with tab3:
    st.subheader("📘 Trade Log & Performance Summary")

    col1, col2, col3 = st.columns(3)
    col1.metric("📂 Total Trades", len(trade_log))
    col2.metric("🔓 Open Trades", len(open_trades))
    col3.metric("💰 Closed PnL", f"{total_pnl:+.2f}")

    if trade_log:
        df = pd.DataFrame(trade_log)
        df["buy_trade_date"] = pd.to_datetime(df["buy_trade_date"])
        df["sell_trade_date"] = pd.to_datetime(df["sell_trade_date"], errors='coerce')
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

        # 📊 Profit vs Loss distribution
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

        # 📋 Show table again
        st.markdown("### 📋 Trade Table")
        st.dataframe(
            df[[
                "symbol", "buy_type", "buy_trade_date", "buy_price",
                "sell_trade_date", "sell_price", "pnl", "status"
            ]].sort_values(by="buy_trade_date", ascending=False),
            use_container_width=True,
        )
    else:
        st.info("No trades logged yet.")

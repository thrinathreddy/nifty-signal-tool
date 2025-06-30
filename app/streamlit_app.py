import streamlit as st
from core.db_handler import get_signals
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.db_handler import get_signals

st.set_page_config(page_title="Nifty50 Signal Dashboard", layout="centered")

st.title("📈 Nifty50 Signal Dashboard")
st.markdown("Displays short-term and long-term BUY signals based on daily scans and fundamentals.")

# Load signals from SQLite database
signals = get_signals()

if signals:
    # Group by type
    short_term = [s for s in signals if s[2] == "BUY"]
    long_term = [s for s in signals if s[2] == "LONG_TERM_BUY"]

    tab1, tab2 = st.tabs(["📅 Short-Term Signals", "🏦 Long-Term Investment Picks"])

    with tab1:
        if short_term:
            st.success(f"{len(short_term)} short-term BUY signals found.")
            for s in short_term:
                st.markdown(f"🔹 **{s[0]}** — `{s[1]}`")
        else:
            st.info("No short-term signals available.")

    with tab2:
        if long_term:
            st.success(f"{len(long_term)} long-term BUY signals found.")
            for s in long_term:
                st.markdown(f"🏆 **{s[0]}** — `{s[1]}`")
        else:
            st.info("No long-term signals available.")
else:
    st.warning("No signals found. Run the `run_daily.py` script or wait for GitHub Actions to trigger.")

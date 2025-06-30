import streamlit as st
import os
import sys

# Add project root to sys.path to fix imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.db_handler import get_signals

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

# Load signals from SQLite DB
signals = get_signals()

# Separate by type
short_term = [s for s in signals if s[2] == "BUY"]
long_term = [s for s in signals if s[2] == "LONG_TERM_BUY"]

# Show tabs
tab1, tab2 = st.tabs(["📅 Short-Term Signals", "🏦 Long-Term Investment Picks"])

# --- TAB 1: SHORT TERM SIGNALS ---
with tab1:
    st.subheader("Today's Technical BUY Signals")
    if short_term:
        st.success(f"📊 {len(short_term)} short-term opportunities found.")
        for sym, date, _ in short_term:
            st.markdown(f"🔹 **{sym}** — `{date}`")
    else:
        st.info("No short-term signals available yet. Run the scanner to generate signals.")

# --- TAB 2: LONG TERM SIGNALS ---
with tab2:
    st.subheader("Long-Term Investment Picks")
    if long_term:
        st.success(f"🏆 {len(long_term)} fundamentally strong stocks identified.")
        for sym, date, _ in long_term:
            st.markdown(f"✅ **{sym}** — `{date}`")
    else:
        st.info("No long-term picks available yet. Try rerunning the fundamental analyzer.")

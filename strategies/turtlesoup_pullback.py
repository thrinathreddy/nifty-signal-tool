# turtlesoup_pullback.py
import pandas as pd

def generate_signal(df):
    if df is None or len(df) < 21:
        return "HOLD"

    latest = df.iloc[-1]
    yesterday = df.iloc[-2]
    lowest_20 = df["low"].iloc[-21:-1].min()

    # Turtle Soup Logic
    turtle_buy = yesterday["low"] < lowest_20 and latest["close"] > yesterday["low"]

    # Pullback + Momentum Confirmation
    pullback_buy = latest["rsi"] > 40 and latest["close"] > df["ema20"].iloc[-1]

    if turtle_buy and pullback_buy:
        return "BUY"
    return "HOLD"

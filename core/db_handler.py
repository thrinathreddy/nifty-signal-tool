import sqlite3
from datetime import date
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "db", "signals.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS signals (
            symbol TEXT, date TEXT, type TEXT
        )
    """)
    conn.commit()
    conn.close()

def save_signal(symbol, signal_type):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO signals VALUES (?, ?, ?)", (symbol, str(date.today()), signal_type))
    conn.commit()
    conn.close()

def get_signals():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM signals ORDER BY date DESC")
    rows = cursor.fetchall()
    conn.close()
    return rows

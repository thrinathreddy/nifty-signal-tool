import sqlite3
from datetime import date

conn = sqlite3.connect("db/signals.db")
cursor = conn.cursor()
cursor.execute("""
    CREATE TABLE IF NOT EXISTS signals (
        symbol TEXT, date TEXT, type TEXT
    )
""")

def save_signal(symbol, signal_type):
    cursor.execute("INSERT INTO signals VALUES (?, ?, ?)", (symbol, str(date.today()), signal_type))
    conn.commit()

def get_signals():
    return cursor.execute("SELECT * FROM signals ORDER BY date DESC").fetchall()

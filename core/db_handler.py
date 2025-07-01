from supabase import create_client
import os
from datetime import date

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def save_signal(symbol, signal_type):
    supabase.table("signals").insert({
        "symbol": symbol,
        "date": str(date.today()),
        "type": signal_type
    }).execute()

def get_signals():
    response = supabase.table("signals").select("*").order("date", desc=True).execute()
    print(response)
    return response.data

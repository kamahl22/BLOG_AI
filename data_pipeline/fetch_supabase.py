from supabase import create_client
from dotenv import load_dotenv
import os

def fetch_supabase_data():
    load_dotenv()

    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")

    if not url or not key:
        print("❌ Missing Supabase URL or Key.")
        return None

    supabase = create_client(url, key)

    try:
        response = supabase.table("odds_data").select("*").execute()
        return response.data
    except Exception as e:
        print("❌ Error fetching data from Supabase:", e)
        return None
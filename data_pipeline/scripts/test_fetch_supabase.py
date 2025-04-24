import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from data_pipeline.fetch_supabase import fetch_supabase_data

def test_fetch_supabase():
    print("🔄 Running test_fetch_supabase...")

    data = fetch_supabase_data()

    if data:
        print("✅ Data retrieved from Supabase:")
        for i, item in enumerate(data):
            print(f"{i+1}. {item}")
    else:
        print("⚠️ No data found or query returned an empty result.")

if __name__ == "__main__":
    test_fetch_supabase()
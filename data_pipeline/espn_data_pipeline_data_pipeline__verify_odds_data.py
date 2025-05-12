from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv()

def verify_odds_data_table():
    try:
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_KEY")
        if not supabase_url or not supabase_key:
            raise ValueError("Supabase URL or Key not set in .env")
        supabase = create_client(supabase_url, supabase_key)

        # Check table structure
        schema_query = """
        SELECT column_name, data_type, is_nullable, column_default
        FROM information_schema.columns
        WHERE table_schema = 'public' AND table_name = 'odds_data'
        """
        schema_result = supabase.rpc("execute_sql", {"query": schema_query}).execute()
        print("Table structure:")
        for row in schema_result.data:
            print(row)

        # Check table data
        data_result = supabase.table("odds_data").select("*").execute()
        print("\nTable data:")
        print(data_result.data if data_result.data else "No data found")

    except Exception as e:
        print(f"Error verifying odds_data: {str(e)}")

if __name__ == "__main__":
    verify_odds_data_table()
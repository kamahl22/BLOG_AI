from supabase import create_client
import os
import pytest
from dotenv import load_dotenv

load_dotenv()

def test_fetch_supabase():
    try:
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_KEY")
        if not supabase_url or not supabase_key:
            pytest.fail("Supabase URL or Key not set in .env")
        supabase = create_client(supabase_url, supabase_key)
        response = supabase.table("odds_data").select("*").execute()
        print(f"Supabase response: {response.data}")
        assert response.data is not None, "Query returned None"
        assert isinstance(response.data, list), "Expected list of records"
    except Exception as e:
        pytest.fail(f"Error fetching data from Supabase: {str(e)}")
from dotenv import load_dotenv
import os
from supabase import create_client, Client
from typing import List, Dict

# Load environment variables from .env file in the same directory
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))

# Retrieve credentials
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Validate credentials
if not SUPABASE_URL or not SUPABASE_KEY:
    raise Exception("Missing SUPABASE_URL or SUPABASE_KEY in environment variables.")

# Create Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def insert_rows(table_name: str, rows: List[Dict]):
    """Insert multiple rows into a Supabase table."""
    if not rows:
        print(f"[SKIP] No data to insert into table '{table_name}'.")
        return
    response = supabase.table(table_name).insert(rows).execute()
    print(f"[INSERT] Inserted {len(rows)} rows into '{table_name}'.")

def delete_existing_team_split_data(table_name: str, team_name: str, stat_type: str):
    """Delete existing rows from a Supabase table by team and stat_type."""
    response = supabase.table(table_name) \
        .delete() \
        .eq("team_name", team_name) \
        .eq("stat_type", stat_type) \
        .execute()
    print(f"[DELETE] Deleted old rows from '{table_name}' for team '{team_name}' and stat_type '{stat_type}'.")
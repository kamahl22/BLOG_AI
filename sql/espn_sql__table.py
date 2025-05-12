import os
from dotenv import load_dotenv

# Get path to the parent directory (where .env is)
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
dotenv_path = os.path.join(parent_dir, '.env')

# Load the .env file from parent directory
load_dotenv(dotenv_path=dotenv_path)

# Now load your credentials
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

print(f"✅ Loaded URL: {SUPABASE_URL}")  # Debug print — should show correct URL

from supabase import create_client, Client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)

def create_table(name: str, schema: str):
    try:
        response = supabase.table(name).insert({}).execute()
        print(f"✅ Table '{name}' exists or is ready.")
    except Exception as e:
        print(f"⚠️ Could not validate or create table '{name}': {e}")

def create_espn_tables():
    tables = {
        "espn_team_stats": """
            CREATE TABLE IF NOT EXISTS espn_team_stats (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                team_name TEXT,
                season_year INT,
                category TEXT,
                stat_name TEXT,
                stat_value TEXT,
                scraped_at TIMESTAMP DEFAULT current_timestamp
            );
        """,
        "espn_team_splits": """
            CREATE TABLE IF NOT EXISTS espn_team_splits (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                team_name TEXT,
                season_year INT,
                split_category TEXT,
                stat_name TEXT,
                stat_value TEXT,
                scraped_at TIMESTAMP DEFAULT current_timestamp
            );
        """,
        "espn_team_injuries": """
            CREATE TABLE IF NOT EXISTS espn_team_injuries (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                team_name TEXT,
                player_name TEXT,
                position TEXT,
                injury_description TEXT,
                status TEXT,
                updated TEXT,
                scraped_at TIMESTAMP DEFAULT current_timestamp
            );
        """,
        "espn_player_stats": """
            CREATE TABLE IF NOT EXISTS espn_player_stats (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                player_name TEXT,
                player_id TEXT,
                team TEXT,
                season_year INT,
                category TEXT,
                stat_name TEXT,
                stat_value TEXT,
                scraped_at TIMESTAMP DEFAULT current_timestamp
            );
        """,
        "espn_player_splits": """
            CREATE TABLE IF NOT EXISTS espn_player_splits (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                player_name TEXT,
                player_id TEXT,
                split_type TEXT,
                split_label TEXT,
                stat_name TEXT,
                stat_value TEXT,
                season_year INT,
                scraped_at TIMESTAMP DEFAULT current_timestamp
            );
        """,
        "espn_batter_vs_pitcher": """
            CREATE TABLE IF NOT EXISTS espn_batter_vs_pitcher (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                batter_id TEXT,
                batter_name TEXT,
                pitcher_id TEXT,
                pitcher_name TEXT,
                team TEXT,
                stat_name TEXT,
                stat_value TEXT,
                scraped_at TIMESTAMP DEFAULT current_timestamp
            );
        """,
        "espn_player_news": """
            CREATE TABLE IF NOT EXISTS espn_player_news (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                player_id TEXT,
                player_name TEXT,
                headline TEXT,
                news_text TEXT,
                source TEXT,
                published TIMESTAMP,
                scraped_at TIMESTAMP DEFAULT current_timestamp
            );
        """,
        "espn_team_news": """
            CREATE TABLE IF NOT EXISTS espn_team_news (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                team_name TEXT,
                headline TEXT,
                news_text TEXT,
                source TEXT,
                published TIMESTAMP,
                scraped_at TIMESTAMP DEFAULT current_timestamp
            );
        """
    }

    for table_name, ddl in tables.items():
        try:
            response = supabase.rpc("execute_sql", {"sql": ddl}).execute()
            print(f"✅ Table '{table_name}' created successfully.")
        except Exception as e:
            print(f"❌ Failed to create table '{table_name}': {e}")

if __name__ == "__main__":
    create_espn_tables()
from dotenv import load_dotenv
import os
from supabase import create_client, Client

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Define the tables and columns
tables = {
    "teams": {
        "id": "uuid PRIMARY KEY",
        "name": "text",
        "abbreviation": "text",
        "league": "text",
        "division": "text"
    },
    "players": {
        "id": "uuid PRIMARY KEY",
        "name": "text",
        "team_id": "uuid REFERENCES teams(id)",
        "position": "text",
        "batting_hand": "text",
        "throwing_hand": "text",
        "birth_date": "date"
    },
    "team_stats": {
        "id": "uuid PRIMARY KEY",
        "team_id": "uuid REFERENCES teams(id)",
        "season": "text",
        "games_played": "integer",
        "wins": "integer",
        "losses": "integer",
        "runs_scored": "integer",
        "runs_allowed": "integer",
        "batting_avg": "numeric",
        "era": "numeric"
    },
    "player_stats": {
        "id": "uuid PRIMARY KEY",
        "player_id": "uuid REFERENCES players(id)",
        "season": "text",
        "games_played": "integer",
        "at_bats": "integer",
        "hits": "integer",
        "home_runs": "integer",
        "rbis": "integer",
        "batting_avg": "numeric",
        "obp": "numeric",
        "slg": "numeric"
    },
    "game_results": {
        "id": "uuid PRIMARY KEY",
        "date": "date",
        "home_team_id": "uuid REFERENCES teams(id)",
        "away_team_id": "uuid REFERENCES teams(id)",
        "home_score": "integer",
        "away_score": "integer",
        "venue": "text"
    },
    "teamrankings_stats": {
        "id": "uuid PRIMARY KEY",
        "team_id": "uuid REFERENCES teams(id)",
        "season": "text",
        "stat_name": "text",
        "value": "numeric"
    },
    "espn_power_index": {
        "id": "uuid PRIMARY KEY",
        "team_id": "uuid REFERENCES teams(id)",
        "week": "integer",
        "season": "text",
        "ranking": "integer",
        "projected_win_pct": "numeric",
        "projected_record": "text"
    }
}

def create_tables():
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("❌ Missing Supabase URL or Key.")
        return

    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    for table_name, columns in tables.items():
        try:
            columns_sql = ", ".join([f"{name} {datatype}" for name, datatype in columns.items()])
            sql = f"CREATE TABLE IF NOT EXISTS public.{table_name} ({columns_sql});"
            response = supabase.rpc("execute_sql", {"sql": sql}).execute()
            print(f"✅ Table '{table_name}' created.")
        except Exception as e:
            print(f"❌ Failed to create table '{table_name}': {e}")

if __name__ == "__main__":
    create_tables()
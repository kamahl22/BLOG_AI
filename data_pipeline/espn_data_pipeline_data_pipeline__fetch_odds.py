from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv()

def store_mlb_odds():
    supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
    odds = [
        {"team_name": "Chicago Cubs", "opponent": "Milwaukee Brewers", "game_date": "2025-04-25", "moneyline_odds": -120, "spread": 1.5, "over_under": 7.5},
        {"team_name": "New York Yankees", "opponent": "Boston Red Sox", "game_date": "2025-04-25", "moneyline_odds": -150, "spread": -1.5, "over_under": 8.0}
    ]
    for game in odds:
        supabase.table("odds_data").insert(game).execute()
    return len(odds)

if __name__ == "__main__":
    try:
        count = store_mlb_odds()
        print(f"Stored {count} games")
    except Exception as e:
        print(f"Error: {str(e)}")
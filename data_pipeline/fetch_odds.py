from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv()

def store_cubs_odds():
    supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
    odds = {
        "team_name": "Chicago Cubs",
        "opponent": "Milwaukee Brewers",
        "game_date": "2025-04-25",
        "moneyline_odds": -120,
        "spread": 1.5,
        "over_under": 7.5
    }
    response = supabase.table("odds_data").insert(odds).execute()
    return response.data

if __name__ == "__main__":
    try:
        result = store_cubs_odds()
        print(f"Stored odds: {result}")
    except Exception as e:
        print(f"Error: {str(e)}")
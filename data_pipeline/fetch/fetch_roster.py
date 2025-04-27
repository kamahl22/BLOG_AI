import requests
from bs4 import BeautifulSoup
from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv()

def fetch_mlb_roster(team_code, team_name):
    url = f"https://www.espn.com/mlb/team/roster/_/name/{team_code}"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    players = []
    table = soup.find("table", class_="Table")
    if table:
        for row in table.find_all("tr")[1:]:
            cols = row.find_all("td")
            if len(cols) >= 6:
                players.append({
                    "team_name": team_name,
                    "player_name": cols[1].text.strip(),
                    "position": cols[2].text.strip(),
                    "age": int(cols[5].text.strip()) if cols[5].text.strip() else None
                })
    supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
    for player in players:
        supabase.table("roster_data").insert(player).execute()
    return len(players)

if __name__ == "__main__":
    try:
        teams = [("chc", "Chicago Cubs"), ("nyy", "New York Yankees")]
        for code, name in teams:
            count = fetch_mlb_roster(code, name)
            print(f"Stored {count} players for {name}")
    except Exception as e:
        print(f"Error: {str(e)}")
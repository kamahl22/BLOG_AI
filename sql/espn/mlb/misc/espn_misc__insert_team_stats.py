import os
import requests
from bs4 import BeautifulSoup
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def scrape_team_stats():
    print("📡 Fetching ESPN team batting stats from HTML...")

    url = "https://www.espn.com/mlb/team/stats/_/name/ari"  # Diamondbacks team stats
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    # ESPN tables often use <table> with <thead> and <tbody>
    tables = soup.find_all("table")

    target_table = None
    for table in tables:
        headers = [th.get_text(strip=True) for th in table.find_all("th")]
        if "GP" in headers and "AVG" in headers and "OPS" in headers:
            target_table = table
            break

    if not target_table:
        raise ValueError("❌ Could not find the batting stats table on ESPN page.")

    rows = target_table.find_all("tr")[2:7]  # Skip header and total row, take 5 players
    results = []

    for row in rows:
        cols = row.find_all("td")
        if len(cols) < 17:
            continue  # Skip malformed rows

        try:
            player_data = {
                "team_name": "Diamondbacks",
                "player_name": cols[0].get_text(strip=True),
                "games_played": int(cols[1].get_text(strip=True)),
                "at_bats": int(cols[2].get_text(strip=True)),
                "runs": int(cols[3].get_text(strip=True)),
                "hits": int(cols[4].get_text(strip=True)),
                "doubles": int(cols[5].get_text(strip=True)),
                "triples": int(cols[6].get_text(strip=True)),
                "home_runs": int(cols[7].get_text(strip=True)),
                "rbi": int(cols[8].get_text(strip=True)),
                "total_bases": int(cols[9].get_text(strip=True)),
                "walks": int(cols[10].get_text(strip=True)),
                "strikeouts": int(cols[11].get_text(strip=True)),
                "stolen_bases": int(cols[12].get_text(strip=True)),
                "avg": float(cols[13].get_text(strip=True)),
                "obp": float(cols[14].get_text(strip=True)),
                "slg": float(cols[15].get_text(strip=True)),
                "ops": float(cols[16].get_text(strip=True)),
            }
            results.append(player_data)
        except Exception as e:
            print(f"⚠️ Skipping row due to error: {e}")
            continue

    print(f"✅ Scraped {len(results)} player stats.")
    return results

def insert_team_stats(data):
    print("📥 Inserting data into Supabase...")
    for row in data:
        try:
            supabase.table("espn_team_stats").insert(row).execute()
            print(f"✅ Inserted: {row['team_name']}")
        except Exception as e:
            print(f"❌ Failed to insert {row['team_name']}: {e}")

if __name__ == "__main__":
    try:
        data = scrape_team_stats()
        if not data:
            print("⚠️ No data scraped. Exiting.")
        else:
            insert_team_stats(data)
            print("🎉 Done!")
    except Exception as e:
        print(f"❌ An error occurred: {e}")
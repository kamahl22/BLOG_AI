import os
import requests
import csv
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from supabase import create_client, Client
from dotenv import load_dotenv

# Base directory for MLB stats
BASE_DIR = "/Users/kamahl/BLOG_AI/Sports/scripts/espn/mlb"
os.makedirs(BASE_DIR, exist_ok=True)

# Load environment variables
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def fetch_team_stats_api():
    """Attempt to fetch MLB team stats via ESPN API."""
    url = "https://site.api.espn.com/apis/site/v2/sports/baseball/mlb/teams"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    }
    response = requests.get(url, headers=headers)
    
    print(f"API Status Code: {response.status_code}")
    if response.status_code != 200:
        print(f"Failed to fetch API data: {response.status_code}")
        return None
    
    data = response.json()
    teams = data.get("sports", [{}])[0].get("leagues", [{}])[0].get("teams", [])
    
    results = []
    for team_data in teams[:5]:  # Limit to top 5 teams
        team = team_data.get("team", {})
        stats = team.get("record", {}).get("stats", [])
        team_name = team.get("displayName", "N/A")
        
        # Extract stats (these keys may need adjustment based on API response)
        games_played = next((s["value"] for s in stats if s["name"] == "gamesPlayed"), 0)
        runs_per_game = next((s["value"] for s in stats if s["name"] == "runsPerGame"), 0.0)
        batting_average = next((s["value"] for s in stats if s["name"] == "battingAverage"), 0.0)
        
        team_data = {
            "team_name": team_name,
            "games_played": int(games_played),
            "runs_per_game": float(runs_per_game),
            "batting_average": float(batting_average),
        }
        print(f"API Scraped data: {team_data}")
        results.append(team_data)
    
    return results if results else None

def scrape_team_stats_html():
    """Fallback to HTML scraping with Selenium if API fails."""
    url = "https://www.espn.com/mlb/stats/team"
    
    # Set up headless Chrome
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("user-agent=Mozilla/5.0")
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    try:
        print("Fetching webpage with Selenium...")
        driver.get(url)
        driver.implicitly_wait(5)
        
        soup = BeautifulSoup(driver.page_source, "html.parser")
        
        # Find the stats table (adjust class based on ESPN's structure)
        table = soup.find("table", class_="Table")
        if not table:
            print("No table found with class 'Table'. Trying first table...")
            table = soup.find("table")
            if not table:
                raise ValueError("Could not find stats table on ESPN page.")
        
        print("Found table, scraping rows...")
        rows = table.find_all("tr")[1:6]  # Get top 5 rows
        print(f"Number of rows found: {len(rows)}")
        
        results = []
        for row in rows:
            cols = row.find_all("td")
            print(f"Processing row with {len(cols)} columns: {[col.text.strip() for col in cols]}")
            if len(cols) < 10:  # Relaxed to account for varying column counts
                print(f"Skipping row: insufficient columns ({len(cols)})")
                continue
            
            try:
                team_data = {
                    "team_name": cols[1].text.strip(),  # Adjust indices after inspecting HTML
                    "games_played": int(cols[2].text.strip()),
                    "runs_per_game": float(cols[4].text.strip()),  # Runs per game may be in a different column
                    "batting_average": float(cols[7].text.strip()),  # Batting average may be in a different column
                }
                print(f"HTML Scraped data: {team_data}")
                results.append(team_data)
            except (ValueError, IndexError) as e:
                print(f"Error processing row: {e}")
                continue
        
        return results
    
    finally:
        driver.quit()

def save_to_csv(data):
    """Save stats to CSV file."""
    csv_path = os.path.join(BASE_DIR, "mlb_team_stats.csv")
    headers = ["team_name", "games_played", "runs_per_game", "batting_average"]
    
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows([[row[h] for h in headers] for row in data])
    
    print(f"CSV file saved: {csv_path}")

def insert_team_stats(data):
    """Insert stats into Supabase."""
    print(f"Inserting {len(data)} records into Supabase...")
    for row in data:
        try:
            supabase.table("espn_team_stats").insert(row).execute()
            print(f"✅ Inserted: {row['team_name']}")
        except Exception as e:
            print(f"❌ Failed to insert {row['team_name']}: {e}")

def main():
    print("Fetching MLB team stats...")
    
    # Try API first
    data = fetch_team_stats_api()
    
    # Fallback to HTML scraping if API fails
    if not data:
        print("API fetch failed, falling back to HTML scraping...")
        data = scrape_team_stats_html()
    
    if not data:
        print("No data scraped. Check API endpoint or HTML structure.")
        return
    
    print(f"Scraped {len(data)} teams")
    
    # Save to CSV
    save_to_csv(data)
    
    # Insert into Supabase
    insert_team_stats(data)
    
    print("Done!")

if __name__ == "__main__":
    main()
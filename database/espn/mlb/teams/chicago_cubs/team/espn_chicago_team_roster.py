from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time
from tabulate import tabulate
import re
import supabase
from dotenv import load_dotenv
import os

load_dotenv()
client = supabase.create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

# Base directory structure
BASE_DIR = "/Users/kamahl/BLOG_AI/database/espn/mlb/teams/chicago_cubs/player"
PLAYER_DIR = os.path.join(BASE_DIR, "player")
TEAM_DIR = os.path.join(BASE_DIR, "team")
os.makedirs(PLAYER_DIR, exist_ok=True)
os.makedirs(TEAM_DIR, exist_ok=True)

# Template scripts for each player with escaped curly braces
PLAYER_SCRIPTS = {
    "espn_chicago_player_splits.py": '''import requests
from bs4 import BeautifulSoup
import csv
import os

player_id = "{player_id}"
player_name = "{player_name}"

def fetch_player_splits():
    url = f"https://www.espn.com/mlb/player/splits/_/id/{{player_id}}/{{player_name.lower().replace(' ', '-')}}"
    headers = {{"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36"}}
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"Error fetching splits for {player_name}: {{response.status_code}}")
        return
    soup = BeautifulSoup(response.text, "html.parser")
    tables = soup.find_all("table")
    if not tables:
        print(f"No splits tables found for {player_name}")
        return
    with open(os.path.join("{player_folder}", "{player_name_lower}_splits.csv"), "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Name", "GP", "IP", "W", "L", "W%", "SV", "SVOP", "BB", "K", "ERA", "OBA", "OOBP", "OSLUG", "OOPS"])
        for table in tables:
            for row in table.find_all("tr")[1:]:
                cols = row.find_all("td")
                if cols:
                    writer.writerow([player_name] + [col.text.strip() for col in cols])
    print(f"Saved splits for {player_name}")

if __name__ == "__main__":
    fetch_player_splits()
''',
    "espn_chicago_player_stats.py": '''import requests
from bs4 import BeautifulSoup
import csv
import os

player_id = "{player_id}"
player_name = "{player_name}"

def fetch_player_stats():
    url = f"https://www.espn.com/mlb/player/stats/_/id/{{player_id}}/{{player_name.lower().replace(' ', '-')}}"
    headers = {{"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36"}}
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"Error fetching stats for {player_name}: {{response.status_code}}")
        return
    soup = BeautifulSoup(response.text, "html.parser")
    tables = soup.find_all("table")
    if not tables:
        print(f"No stats tables found for {player_name}")
        return
    with open(os.path.join("{player_folder}", "{player_name_lower}_stats.csv"), "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Name", "GP", "IP", "W", "L", "ERA", "SO"])
        for table in tables:
            for row in table.find_all("tr")[1:]:
                cols = row.find_all("td")
                if cols:
                    writer.writerow([player_name] + [col.text.strip() for col in cols[:7]])
    print(f"Saved stats for {player_name}")

if __name__ == "__main__":
    fetch_player_stats()
''',
    "espn_chicago_player_news.py": '''import requests
from bs4 import BeautifulSoup
import csv
import os

player_id = "{player_id}"
player_name = "{player_name}"

def fetch_player_news():
    url = f"https://www.espn.com/mlb/player/news/_/id/{{player_id}}/{{player_name.lower().replace(' ', '-')}}"
    headers = {{"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36"}}
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"Error fetching news for {player_name}: {{response.status_code}}")
        return
    soup = BeautifulSoup(response.text, "html.parser")
    articles = soup.find_all("article")
    if not articles:
        print(f"No news found for {player_name}")
        return
    with open(os.path.join("{player_folder}", "{player_name_lower}_news.csv"), "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Name", "Headline", "Date", "Summary"])
        for article in articles:
            headline = article.find("h2")
            date = article.find("time")
            summary = article.find("p")
            writer.writerow([player_name, headline.text.strip() if headline else "", date.text.strip() if date else "", summary.text.strip() if summary else ""])
    print(f"Saved news for {player_name}")

if __name__ == "__main__":
    fetch_player_news()
''',
    "espn_chicago_batter_vs_pitcher.py": '''import requests
from bs4 import BeautifulSoup
import csv
import os

player_id = "{player_id}"
player_name = "{player_name}"

def fetch_batter_vs_pitcher():
    url = f"https://www.espn.com/mlb/player/gamelog/_/id/{{player_id}}/{{player_name.lower().replace(' ', '-')}}"
    headers = {{"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36"}}
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"Error fetching batter vs pitcher for {player_name}: {{response.status_code}}")
        return
    soup = BeautifulSoup(response.text, "html.parser")
    tables = soup.find_all("table")
    if not tables:
        print(f"No batter vs pitcher data found for {player_name}")
        return
    with open(os.path.join("{player_folder}", "{player_name_lower}_batter_vs_pitcher.csv"), "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Name", "Opponent", "Date", "Result"])
        for table in tables:
            for row in table.find_all("tr")[1:]:
                cols = row.find_all("td")
                if cols and len(cols) >= 4:
                    writer.writerow([player_name] + [col.text.strip() for col in cols[:4]])
    print(f"Saved batter vs pitcher for {player_name}")

if __name__ == "__main__":
    fetch_batter_vs_pitcher()
'''
}

def scrape_cubs_roster():
    print("📡 Fetching Chicago Cubs roster...")
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36")
    driver = webdriver.Chrome(options=chrome_options)
    try:
        driver.get("https://www.espn.com/mlb/team/roster/_/name/chc/chicago-cubs")
        print("Page loaded successfully")
        time.sleep(5)
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, "html.parser")
        tables = soup.find_all("table", class_="Table")
        if not tables:
            print("❌ No roster tables found")
            return []
        
        espn_headers = ["Jersey", "Name", "POS", "BAT", "THW", "Age", "HT", "WT", "Birth Place"]
        db_columns = ["team", "jersey", "name", "pos", "bat", "thw", "age", "ht", "wt", "birth_place"]
        db_column_mapping = {h: h.lower().replace(" ", "_") for h in espn_headers}
        index_mapping = {i: db_column_mapping[h] for i, h in enumerate(espn_headers)}
        
        print(f"Using column mapping: {db_column_mapping}")
        print(f"Using index mapping: {index_mapping}")
        
        all_rows = []
        for i, table in enumerate(tables):
            print(f"Processing table {i+1}/{len(tables)}")
            raw_headers = [th.text.strip() for th in table.find("thead").find_all("th")]
            print(f"Raw headers: {raw_headers}")
            for tr in table.find("tbody").find_all("tr"):
                cells = tr.find_all("td")
                if len(cells) < 2:
                    continue
                name_cell = cells[1].text.strip()
                jersey_match = re.search(r'(\d+)$', name_cell)
                jersey = jersey_match.group(1) if jersey_match else ""
                name = re.sub(r'\d+$', '', name_cell).strip()
                row = [jersey, name] + [td.text.strip() for td in cells[2:]]
                print(f"Row: {row}")
                
                row_dict = {"team": "chicago-cubs"}
                for idx, col_name in index_mapping.items():
                    if idx < len(row):
                        if col_name == "age" and row[idx].isdigit():
                            row_dict[col_name] = int(row[idx])
                        else:
                            row_dict[col_name] = row[idx]
                
                all_rows.append(row_dict)
                # Create player folder and scripts
                player_name_dir = name.lower().replace(" ", "_")
                player_folder = os.path.join(PLAYER_DIR, player_name_dir)
                os.makedirs(player_folder, exist_ok=True)
                for script_name, script_content in PLAYER_SCRIPTS.items():
                    formatted_content = script_content.format(
                        player_id="N/A",  # Replace with actual player ID if available
                        player_name=name,
                        player_folder=player_folder,
                        player_name_lower=player_name_dir
                    )
                    script_path = os.path.join(player_folder, script_name)
                    with open(script_path, "w", encoding="utf-8") as f:
                        f.write(formatted_content)
                    print(f"Created script: {script_path}")
        
        if all_rows:
            print("Chicago Cubs Roster:")
            print(tabulate([list(r.values()) for r in all_rows], 
                          headers=list(all_rows[0].keys()), 
                          tablefmt="grid"))
            try:
                client.table("team_roster").delete().eq("team", "chicago-cubs").execute()
                print(f"Inserting {len(all_rows)} rows: {all_rows[:2]}")
                client.table("team_roster").insert(all_rows).execute()
                print("✅ Successfully inserted roster into Supabase")
            except Exception as e:
                print(f"❌ Supabase insertion error: {str(e)}")
        else:
            print("❌ No roster data extracted")
        return all_rows
    except Exception as e:
        print(f"Error scraping roster: {str(e)}")
        import traceback
        traceback.print_exc()
        return []
    finally:
        driver.quit()

if __name__ == "__main__":
    roster = scrape_cubs_roster()
    print(f"✅ Scraped {len(roster)} roster entries." if roster else "❌ No roster data.")
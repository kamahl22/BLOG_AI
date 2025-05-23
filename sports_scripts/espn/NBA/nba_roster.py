import requests
import csv
import os
import logging
from bs4 import BeautifulSoup
from datetime import datetime
from dateutil import parser

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Base directory for MLB data
BASE_DIR = "/Users/kamahl/BLOG_AI/sports/mlb"
os.makedirs(BASE_DIR, exist_ok=True)

# API endpoint for MLB teams
TEAMS_URL = "http://site.api.espn.com/apis/site/v2/sports/baseball/mlb/teams"

def fetch_team_rosters():
    """Fetch rosters for all MLB teams."""
    team_rosters = {}
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    }
    
    try:
        response = requests.get(TEAMS_URL, headers=headers, timeout=10)
        response.raise_for_status()
        teams = response.json().get("sports", [])[0].get("leagues", [])[0].get("teams", [])
    except requests.RequestException as e:
        logger.error(f"Failed to fetch teams: {e}")
        return team_rosters
    
    for team_obj in teams:
        team_info = team_obj.get("team", {})
        team_id = team_info.get("id", "")
        team_city = team_info.get("location", "").lower().replace(" ", "-").replace(".", "")
        team_name = team_info.get("name", "").lower().replace(" ", "-").replace(".", "")
        full_team_name = f"{team_city}-{team_name}"
        
        team_folder = os.path.join(BASE_DIR, full_team_name)
        try:
            os.makedirs(team_folder, exist_ok=True)
        except OSError as e:
            logger.error(f"Failed to create folder {team_folder}: {e}")
            continue
        
        roster_url = f"http://site.api.espn.com/apis/site/v2/sports/baseball/mlb/teams/{team_id}/roster"
        try:
            roster_response = requests.get(roster_url, headers=headers, timeout=10)
            roster_response.raise_for_status()
            roster_data = roster_response.json()
        except requests.RequestException as e:
            logger.warning(f"Failed to fetch roster for {full_team_name} (ID: {team_id}): {e}")
            continue
        
        players = []
        for group in roster_data.get("athletes", []):
            for player in group.get("items", []):
                player_id = player.get("id", "")
                player_name = player.get("fullName", "")
                if player_id and player_name:
                    players.append({"name": player_name, "id": player_id})
        
        team_rosters[full_team_name] = {"team_id": team_id, "players": players}
        logger.info(f"Fetched roster for {full_team_name}: {len(players)} players")
        
        # Save roster to CSV
        roster_csv = os.path.join(team_folder, "roster.csv")
        try:
            with open(roster_csv, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["Player Name", "Player ID"])
                writer.writerows([[p["name"], p["id"]] for p in players])
            logger.info(f"Saved roster CSV: {roster_csv}")
        except OSError as e:
            logger.error(f"Failed to save roster CSV {roster_csv}: {e}")
    
    return team_rosters

def create_player_folders_and_scripts(team_rosters):
    """Create player folders and scripts."""
    # Template for player_splits.py
    splits_template = '''import requests
import csv
import os
from bs4 import BeautifulSoup

player_id = "{player_id}"
player_name = "{player_name}"
player_name_slug = "{player_name_slug}"

def fetch_and_save_data():
    url = f"https://www.espn.com/mlb/player/splits/_/id/{player_id}/{player_name_slug}"
    
    headers = {{
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    }}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error fetching splits for {player_name} (ID: {player_id}): {{e}}")
        return None, None
    
    soup = BeautifulSoup(response.text, "html.parser")
    tables = soup.find_all("table")
    print(f"Found {{len(tables)}} tables")
    
    if not tables:
        print(f"No splits tables found for {player_name}")
        return None, None
    
    expected_headers = ["SPLIT", "G", "AB", "R", "H", "2B", "3B", "HR", "RBI", "BB", "SO", "SB", "CS", "AVG", "OBP", "SLG", "OPS"]
    
    preset_splits = [
        "All Splits", "Home", "Road", "vs AL", "vs NL", "Day", "Night",
        "March/April", "May", "June", "July", "August", "September/October",
        "Pre All-Star", "Post All-Star", "Grass", "Turf",
        "vs LHP", "vs RHP", "Starter", "Reliever"
    ]
    
    default_stats = ["0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", ".000", ".000", ".000", ".000"]
    player_data_dict = {{split: default_stats.copy() for split in preset_splits}}
    
    all_rows = []
    for table in tables:
        all_rows.extend(table.find_all("tr")[1:])
    
    splits = []
    stats_rows = []
    for row in all_rows:
        columns = row.find_all("td")
        row_data = [col.text.strip() for col in columns if col.text.strip()]
        if not row_data:
            continue
        if len(row_data) == 1 and row_data[0] in preset_splits:
            splits.append(row_data[0])
            print(f"Split found: {{row_data[0]}}")
        elif len(row_data) > 1 and row_data[0].isdigit():
            stats_rows.append(row_data)
            print(f"Stats found: {{row_data}}")
    
    for idx, split in enumerate(splits):
        if idx < len(stats_rows):
            stats = stats_rows[idx][:len(expected_headers)-1]
            stats += ["N/A"] * (len(expected_headers)-1 - len(stats)) if len(stats) < len(expected_headers)-1 else []
            player_data_dict[split] = stats
            print(f"Paired {{split}} with {{stats}}")
    
    player_data = [[split] + player_data_dict[split] for split in preset_splits]
    
    if not player_data:
        print(f"No splits data found for {player_name}")
        return None, None
    
    base_directory = "{base_dir}"
    player_folder = os.path.join(base_directory, "{team}", "{player_name_dir}")
    os.makedirs(player_folder, exist_ok=True)
    
    csv_filename = os.path.join(player_folder, f"{player_name_dir}_splits.csv")
    try:
        with open(csv_filename, "w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(expected_headers)
            writer.writerows(player_data)
        print(f"Saved CSV: {{csv_filename}}")
    except OSError as e:
        print(f"Error saving CSV {{csv_filename}}: {{e}}")
        return None, None
    
    return expected_headers, player_data

if __name__ == "__main__":
    headers, data = fetch_and_save_data()
'''

    # Template for player_stats.py
    stats_template = '''import requests
import csv
import os
from bs4 import BeautifulSoup

player_id = "{player_id}"
player_name = "{player_name}"
player_name_slug = "{player_name_slug}"

def fetch_and_save_data():
    url = f"https://www.espn.com/mlb/player/stats/_/id/{player_id}/{player_name_slug}"
    
    headers = {{
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    }}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error fetching stats for {player_name} (ID: {player_id}): {{e}}")
        return None, None
    
    soup = BeautifulSoup(response.text, "html.parser")
    tables = soup.find_all("table")
    print(f"Found {{len(tables)}} tables")
    
    if not tables:
        print(f"No stats tables found for {player_name}")
        return None, None
    
    expected_headers = ["SEASON", "TEAM", "G", "AB", "R", "H", "2B", "3B", "HR", "RBI", "BB", "SO", "SB", "CS", "AVG", "OBP", "SLG", "OPS"]
    
    player_data = []
    for table in tables:
        rows = table.find_all("tr")[1:]  # Skip header
        for row in rows:
            columns = row.find_all("td")
            row_data = [col.text.strip() for col in columns if col.text.strip()]
            if row_data and len(row_data) >= 2:  # Ensure at least SEASON and TEAM
                stats = row_data[:len(expected_headers)-1]
                stats += ["N/A"] * (len(expected_headers)-1 - len(stats)) if len(stats) < len(expected_headers)-1 else []
                player_data.append(stats)
    
    if not player_data:
        print(f"No stats data found for {player_name}")
        return None, None
    
    base_directory = "{base_dir}"
    player_folder = os.path.join(base_directory, "{team}", "{player_name_dir}")
    os.makedirs(player_folder, exist_ok=True)
    
    csv_filename = os.path.join(player_folder, f"{player_name_dir}_stats.csv")
    try:
        with open(csv_filename, "w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(expected_headers)
            writer.writerows(player_data)
        print(f"Saved CSV: {{csv_filename}}")
    except OSError as e:
        print(f"Error saving CSV {{csv_filename}}: {{e}}")
        return None, None
    
    return expected_headers, player_data

if __name__ == "__main__":
    headers, data = fetch_and_save_data()
'''

    # Template for player_batvspitch.py
    batvspitch_template = '''import requests
import csv
import os
from bs4 import BeautifulSoup

player_id = "{player_id}"
player_name = "{player_name}"
team_id = "{team_id}"

def fetch_and_save_data():
    url = f"https://www.espn.com/mlb/player/batvspitch/_/id/{player_id}/teamId/{team_id}"
    
    headers = {{
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    }}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error fetching bat vs pitch for {player_name} (ID: {player_id}): {{e}}")
        return None, None
    
    soup = BeautifulSoup(response.text, "html.parser")
    tables = soup.find_all("div", class_="ResponsiveTable")
    
    if not tables:
        print(f"No bat vs pitch tables found for {player_name}")
        return None, None
    
    expected_headers = ["PITCHER", "AB", "H", "2B", "3B", "HR", "RBI", "BB", "SO", "AVG", "OBP", "SLG", "OPS"]
    
    player_data = []
    for table in tables:
        tbody = table.find("tbody")
        if not tbody:
            continue
        rows = tbody.find_all("tr")
        for row in rows:
            cells = row.find_all("td")
            if not cells or len(cells) <= 1:
                continue
            row_data = [cell.text.strip() for cell in cells]
            if row_data[0].lower() == "totals":
                continue
            stats = row_data[:len(expected_headers)-1]
            stats += ["N/A"] * (len(expected_headers)-1 - len(stats)) if len(stats) < len(expected_headers)-1 else []
            player_data.append(stats)
    
    if not player_data:
        print(f"No bat vs pitch data found for {player_name}")
        return None, None
    
    base_directory = "{base_dir}"
    player_folder = os.path.join(base_directory, "{team}", "{player_name_dir}")
    os.makedirs(player_folder, exist_ok=True)
    
    csv_filename = os.path.join(player_folder, f"{player_name_dir}_batvspitch.csv")
    try:
        with open(csv_filename, "w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(expected_headers)
            writer.writerows(player_data)
        print(f"Saved CSV: {{csv_filename}}")
    except OSError as e:
        print(f"Error saving CSV {{csv_filename}}: {{e}}")
        return None, None
    
    return expected_headers, player_data

if __name__ == "__main__":
    headers, data = fetch_and_save_data()
'''

    # Template for player_gamelog.py
    gamelog_template = '''import requests
import csv
import os
from datetime import datetime
from dateutil import parser

player_id = "{player_id}"
player_name = "{player_name}"
team_id = "{team_id}"

def fetch_and_save_data():
    url = f"https://site.web.api.espn.com/apis/common/v3/sports/baseball/mlb/athletes/{player_id}/gamelog?season=2025"
    
    headers = {{
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    }}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
    except requests.RequestException as e:
        print(f"Error fetching gamelog for {player_name} (ID: {player_id}): {{e}}")
        return None, None
    
    expected_headers = ["DATE", "OPPONENT", "RESULT", "AB", "R", "H", "2B", "3B", "HR", "RBI", "BB", "SO", "SB", "CS", "AVG", "OBP", "SLG", "OPS"]
    
    player_data = []
    events_dict = data.get('events', {})
    for game_id, event in events_dict.items():
        game_date = parser.parse(event.get('gameDate', '')).strftime("%Y-%m-%d") if event.get('gameDate') else 'N/A'
        opponent = event.get('opponent', {}).get('displayName', 'Unknown')
        home_score = event.get('homeTeamScore', 0)
        away_score = event.get('awayTeamScore', 0)
        home_team_id = event.get('homeTeamId', '')
        result = 'N/A'
        if home_score is not None and away_score is not None and home_team_id:
            if home_team_id == team_id:
                result = f"W {home_score}-{away_score}" if int(home_score) > int(away_score) else f"L {home_score}-{away_score}"
            else:
                result = f"W {away_score}-{home_score}" if int(away_score) > int(home_score) else f"L {away_score}-{home_score}"
        
        stats = event.get('stats', [])
        row_data = [game_date, opponent, result]
        stat_fields = ["AB", "R", "H", "2B", "3B", "HR", "RBI", "BB", "SO", "SB", "CS", "AVG", "OBP", "SLG", "OPS"]
        for i, field in enumerate(stat_fields):
            row_data.append(stats[i] if i < len(stats) else "N/A")
        
        player_data.append(row_data)
    
    if not player_data:
        print(f"No gamelog data found for {player_name}")
        return None, None
    
    base_directory = "{base_dir}"
    player_folder = os.path.join(base_directory, "{team}", "{player_name_dir}")
    os.makedirs(player_folder, exist_ok=True)
    
    csv_filename = os.path.join(player_folder, f"{player_name_dir}_gamelog.csv")
    try:
        with open(csv_filename, "w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(expected_headers)
            writer.writerows(player_data)
        print(f"Saved CSV: {{csv_filename}}")
    except OSError as e:
        print(f"Error saving CSV {{csv_filename}}: {{e}}")
        return None, None
    
    return expected_headers, player_data

if __name__ == "__main__":
    headers, data = fetch_and_save_data()
'''

    for team, team_data in team_rosters.items():
        team_id = team_data["team_id"]
        players = team_data["players"]
        team_folder = os.path.join(BASE_DIR, team)
        for player in players:
            player_name = player["name"]
            player_id = player["id"]
            # Sanitize player name for folder and URL
            player_name_dir = player_name.lower().replace(" ", "_").replace(".", "").replace("'", "").encode('ascii', 'ignore').decode('ascii')
            player_name_slug = player_name.lower().replace(" ", "-").replace(".", "").replace("'", "").encode('ascii', 'ignore').decode('ascii')
            player_folder = os.path.join(team_folder, player_name_dir)
            try:
                os.makedirs(player_folder, exist_ok=True)
            except OSError as e:
                logger.error(f"Failed to create folder {player_folder}: {e}")
                continue
            
            scripts = [
                ("splits", splits_template),
                ("stats", stats_template),
                ("batvspitch", batvspitch_template),
                ("gamelog", gamelog_template)
            ]
            
            for script_type, template in scripts:
                try:
                    script_content = template.format(
                        player_id=player_id,
                        player_name=player_name,
                        player_name_slug=player_name_slug,
                        team_id=team_id or "N/A",
                        base_dir=BASE_DIR,
                        team=team,
                        player_name_dir=player_name_dir
                    )
                    script_path = os.path.join(player_folder, f"{player_name_dir}_{script_type}.py")
                    with open(script_path, "w", encoding="utf-8") as f:
                        f.write(script_content)
                    logger.info(f"Created script: {script_path}")
                except (OSError, ValueError, KeyError, IndexError) as e:
                    logger.error(f"Failed to create script {script_path} for {player_name}: {e}")
                    continue

def main():
    """Update MLB team rosters and create player folders/scripts."""
    logger.info("Starting MLB roster update...")
    team_rosters = fetch_team_rosters()
    if not team_rosters:
        logger.error("No rosters found. Exiting.")
        return
    logger.info("Creating player folders and scripts...")
    create_player_folders_and_scripts(team_rosters)
    logger.info("MLB roster update complete.")

if __name__ == "__main__":
    main()
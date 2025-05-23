import requests
import csv
import os
from bs4 import BeautifulSoup

# Base directory for MLB data
BASE_DIR = "/Users/kamahl/BLOG_AI/sports/mlb"
os.makedirs(BASE_DIR, exist_ok=True)

# API endpoint to get all MLB teams
TEAMS_URL = "http://site.api.espn.com/apis/site/v2/sports/baseball/mlb/teams"

def fetch_team_rosters():
    """Fetch updated rosters for all MLB teams."""
    team_rosters = {}
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    }
    
    response = requests.get(TEAMS_URL, headers=headers)
    if not response.ok:
        print(f"Failed to fetch teams: {response.status_code}")
        return team_rosters
    
    teams = response.json().get("sports", [])[0].get("leagues", [])[0].get("teams", [])
    
    for team_obj in teams:
        team_info = team_obj.get("team", {})
        team_id = team_info.get("id", "")
        team_city = team_info.get("location", "").lower().replace(" ", "-")
        team_name = team_info.get("name", "").lower().replace(" ", "-")
        full_team_name = f"{team_city}-{team_name}"
        
        team_folder = os.path.join(BASE_DIR, full_team_name)
        os.makedirs(team_folder, exist_ok=True)
        
        roster_url = f"http://site.api.espn.com/apis/site/v2/sports/baseball/mlb/teams/{team_id}/roster"
        roster_response = requests.get(roster_url, headers=headers)
        if not roster_response.ok:
            print(f"Failed to fetch roster for team ID {team_id}: {roster_response.status_code}")
            continue
        
        roster_data = roster_response.json()
        players = []
        for group in roster_data.get("athletes", []):
            for player in group.get("items", []):
                player_id = player.get("id", "N/A")
                player_name = player.get("fullName", "N/A")
                if player_id != "N/A" and player_name != "N/A":
                    players.append({"name": player_name, "id": player_id})
        
        team_rosters[full_team_name] = {"team_id": team_id, "players": players}
        print(f"Fetched roster for {full_team_name}: {len(players)} players")
        
        # Save roster to CSV
        roster_csv = os.path.join(team_folder, "roster.csv")
        with open(roster_csv, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Player Name", "Player ID"])
            writer.writerows([[p["name"], p["id"]] for p in players])
    
    return team_rosters

def create_player_folders_and_scripts(team_rosters):
    """Create folders and scripts for each player."""
    # Template for player_splits.py
    splits_template = '''import requests
import csv
import os
from bs4 import BeautifulSoup

player_id = "{player_id}"
player_name = "{player_name}"

def fetch_and_save_data():
    url = f"https://www.espn.com/mlb/player/splits/_/id/{{player_id}}/{{player_name.lower().replace(' ', '-')}}"
    
    headers = {{
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    }}
    response = requests.get(url, headers=headers)
    
    print(f"Status Code: {{response.status_code}}")
    if response.status_code != 200:
        print(f"Error: Unable to fetch data for {{player_name}} (ID: {{player_id}}) - Status Code {{response.status_code}}")
        return None, None
    
    soup = BeautifulSoup(response.text, "html.parser")
    tables = soup.find_all("table")
    print(f"Number of tables found: {{len(tables)}}")
    
    if not tables:
        print(f"No stats tables found for {{player_name}}. The page structure may have changed.")
        return None, None
    
    expected_headers = ["SPLIT", "G", "AB", "R", "H", "2B", "3B", "HR", "RBI", "BB", "SO", "SB", "CS", "AVG", "OBP", "SLG", "OPS"]
    
    preset_splits = [
        "All Splits", "Home", "Road", "vs AL", "vs NL", "Day", "Night",
        "April", "May", "June", "July", "August", "September",
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
    for i, row in enumerate(all_rows):
        columns = row.find_all("td")
        row_data = [col.text.strip() for col in columns if col.text.strip()]
        if not row_data:
            continue
        if len(row_data) == 1 and row_data[0] in preset_splits:
            splits.append(row_data[0])
            print(f"Split found ({{len(splits)-1}}): ['{{row_data[0]}}']")
        elif len(row_data) > 1 and row_data[0].isdigit():
            stats_rows.append(row_data)
            print(f"Stats found ({{len(stats_rows)-1}}): {{row_data}}")
        else:
            print(f"Subheader: {{row_data}}")
        print()
    
    for idx, split in enumerate(splits):
        if idx < len(stats_rows):
            stats = stats_rows[idx][:len(expected_headers)-1] + ["N/A" for _ in range(len(stats_rows[idx]), len(expected_headers)-1)] if len(stats_rows[idx]) < len(expected_headers)-1 else stats_rows[idx][:len(expected_headers)-1]
            player_data_dict[split] = stats
            print(f"Paired: ['{{split}}'] with {{stats}}")
            print()
    
    player_data = [[split] + player_data_dict[split] for split in preset_splits]
    
    if not player_data:
        print(f"No player splits data found for {{player_name}}.")
        return None, None
    
    base_directory = "{base_dir}"
    player_folder = os.path.join(base_directory, "{team}", "{player_name_dir}")
    os.makedirs(player_folder, exist_ok=True)
    
    csv_filename = os.path.join(player_folder, f"{{player_name.lower().replace(' ', '_')}}_splits.csv")
    with open(csv_filename, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(expected_headers)
        writer.writerows(player_data)
    
    print(f"CSV file saved: {{csv_filename}}")
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

def fetch_and_save_data():
    url = f"https://www.espn.com/mlb/player/stats/_/id/{{player_id}}/{{player_name.lower().replace(' ', '-')}}"
    
    headers = {{
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    }}
    response = requests.get(url, headers=headers)
    
    print(f"Status Code: {{response.status_code}}")
    if response.status_code != 200:
        print(f"Error: Unable to fetch data for {{player_name}} (ID: {{player_id}}) - Status Code {{response.status_code}}")
        return None, None
    
    soup = BeautifulSoup(response.text, "html.parser")
    tables = soup.find_all("table")
    print(f"Number of tables found: {{len(tables)}}")
    
    if not tables:
        print(f"No stats tables found for {{player_name}}. The page structure may have changed.")
        return None, None
    
    expected_headers = ["SEASON", "TEAM", "G", "AB", "R", "H", "2B", "3B", "HR", "RBI", "BB", "SO", "SB", "CS", "AVG", "OBP", "SLG", "OPS"]
    
    player_data = []
    for table in tables:
        rows = table.find_all("tr")[1:]  # Skip header
        for row in rows:
            columns = row.find_all("td")
            row_data = [col.text.strip() for col in columns if col.text.strip()]
            if row_data and len(row_data) >= len(expected_headers) - 1:
                player_data.append(row_data[:len(expected_headers)-1] + ["N/A" for _ in range(len(row_data), len(expected_headers)-1)])
    
    if not player_data:
        print(f"No player stats data found for {{player_name}}.")
        return None, None
    
    base_directory = "{base_dir}"
    player_folder = os.path.join(base_directory, "{team}", "{player_name_dir}")
    os.makedirs(player_folder, exist_ok=True)
    
    csv_filename = os.path.join(player_folder, f"{{player_name.lower().replace(' ', '_')}}_stats.csv")
    with open(csv_filename, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(expected_headers)
        writer.writerows(player_data)
    
    print(f"CSV file saved: {{csv_filename}}")
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
    url = f"https://www.espn.com/mlb/player/batvspitch/_/id/{{player_id}}/teamId/{{team_id}}"
    
    headers = {{
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    }}
    response = requests.get(url, headers=headers)
    
    print(f"Status Code: {{response.status_code}}")
    if response.status_code != 200:
        print(f"Error: Unable to fetch data for {{player_name}} (ID: {{player_id}}) - Status Code {{response.status_code}}")
        return None, None
    
    soup = BeautifulSoup(response.text, "html.parser")
    tables = soup.find_all("div", class_="ResponsiveTable")
    
    if not tables:
        print(f"No stats tables found for {{player_name}}. The page structure may have changed.")
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
            if row_data[0] == "Totals":
                continue
            if len(row_data) >= len(expected_headers) - 1:
                player_data.append(row_data[:len(expected_headers)-1] + ["N/A" for _ in range(len(row_data), len(expected_headers)-1)])
    
    if not player_data:
        print(f"No bat vs pitch data found for {{player_name}}.")
        return None, None
    
    base_directory = "{base_dir}"
    player_folder = os.path.join(base_directory, "{team}", "{player_name_dir}")
    os.makedirs(player_folder, exist_ok=True)
    
    csv_filename = os.path.join(player_folder, f"{{player_name.lower().replace(' ', '_')}}_batvspitch.csv")
    with open(csv_filename, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(expected_headers)
        writer.writerows(player_data)
    
    print(f"CSV file saved: {{csv_filename}}")
    return expected_headers, player_data

if __name__ == "__main__":
    headers, data = fetch_and_save_data()
'''

    # Template for player_gamelog.py
    gamelog_template = '''import requests
import csv
import os
import json
from datetime import datetime
from dateutil import parser

player_id = "{player_id}"
player_name = "{player_name}"
team_id = "{team_id}"

def fetch_and_save_data():
    url = f"https://site.web.api.espn.com/apis/common/v3/sports/baseball/mlb/athletes/{{player_id}}/gamelog?season=2025"
    
    headers = {{
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    }}
    response = requests.get(url, headers=headers)
    
    print(f"Status Code: {{response.status_code}}")
    if response.status_code != 200:
        print(f"Error: Unable to fetch data for {{player_name}} (ID: {{player_id}}) - Status Code {{response.status_code}}")
        return None, None
    
    data = response.json()
    
    expected_headers = ["DATE", "OPPONENT", "RESULT", "AB", "R", "H", "2B", "3B", "HR", "RBI", "BB", "SO", "SB", "CS", "AVG", "OBP", "SLG", "OPS"]
    
    player_data = []
    events_dict = data.get('events', {})
    for game_id, event in events_dict.items():
        game_date = parser.parse(event.get('gameDate', 'N/A')).strftime("%Y-%m-%d") if event.get('gameDate') else 'N/A'
        opponent = event.get('opponent', {}).get('displayName', 'Unknown')
        home_score = event.get('homeTeamScore', 0)
        away_score = event.get('awayTeamScore', 0)
        home_team_id = event.get('homeTeamId', '')
        result = 'N/A'
        if home_score is not None and away_score is not None:
            if home_team_id == team_id:
                result = f"W {{home_score}}-{{away_score}}" if int(home_score) > int(away_score) else f"L {{home_score}}-{{away_score}}"
            else:
                result = f"W {{away_score}}-{{home_score}}" if int(away_score) > int(home_score) else f"L {{away_score}}-{{home_score}}"
        
        stats = event.get('stats', [])
        row_data = [game_date, opponent, result]
        stat_fields = ["AB", "R", "H", "2B", "3B", "HR", "RBI", "BB", "SO", "SB", "CS", "AVG", "OBP", "SLG", "OPS"]
        for i, field in enumerate(stat_fields):
            row_data.append(stats[i] if i < len(stats) else "N/A")
        
        player_data.append(row_data)
    
    if not player_data:
        print(f"No gamelog data found for {{player_name}}.")
        return None, None
    
    base_directory = "{base_dir}"
    player_folder = os.path.join(base_directory, "{team}", "{player_name_dir}")
    os.makedirs(player_folder, exist_ok=True)
    
    csv_filename = os.path.join(player_folder, f"{{player_name.lower().replace(' ', '_')}}_gamelog.csv")
    with open(csv_filename, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(expected_headers)
        writer.writerows(player_data)
    
    print(f"CSV file saved: {{csv_filename}}")
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
            player_name_dir = player_name.lower().replace(" ", "_")
            player_folder = os.path.join(team_folder, player_name_dir)
            os.makedirs(player_folder, exist_ok=True)
            
            # Generate scripts
            scripts = [
                ("splits", splits_template),
                ("stats", stats_template),
                ("batvspitch", batvspitch_template),
                ("gamelog", gamelog_template)
            ]
            
            for script_type, template in scripts:
                script_content = template.format(
                    player_id=player_id,
                    player_name=player_name,
                    team_id=team_id or "N/A",
                    base_dir=BASE_DIR,
                    team=team,
                    player_name_dir=player_name_dir
                )
                script_path = os.path.join(player_folder, f"{player_name_dir}_{script_type}.py")
                with open(script_path, "w", encoding="utf-8") as f:
                    f.write(script_content)
                print(f"Created script: {script_path}")

def main():
    """Main function to update MLB team rosters and create player folders/scripts."""
    print("Updating MLB team rosters...")
    team_rosters = fetch_team_rosters()
    if not team_rosters:
        print("No rosters found. Exiting.")
        return
    print("Creating player folders and scripts...")
    create_player_folders_and_scripts(team_rosters)
    print("Done!")

if __name__ == "__main__":
    main()

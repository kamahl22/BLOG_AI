import requests
import csv
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Base directory for MLB data
BASE_DIR = "/Users/kamahl/BLOG_AI/espn/mlb"
os.makedirs(BASE_DIR, exist_ok=True)

# API endpoints
TEAMS_URL = "http://site.api.espn.com/apis/site/v2/sports/baseball/mlb/teams"

def fetch_team_rosters():
    """Fetch rosters for all MLB teams."""
    team_rosters = {}
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    }
    
    # Fetch all teams
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
        
        # Create team folder
        team_folder = os.path.join(BASE_DIR, full_team_name)
        try:
            os.makedirs(team_folder, exist_ok=True)
        except OSError as e:
            logger.error(f"Failed to create folder {team_folder}: {e}")
            continue
        
        # Fetch team roster
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
import pandas as pd
from datetime import datetime
import os

player_id = "{player_id}"
player_name = "{player_name}"
player_name_slug = "{player_name_slug}"

# API endpoint for splits
url = "https://site.web.api.espn.com/apis/common/v3/sports/baseball/mlb/athletes/{player_id}/splits?season=2025"

# Make the API call
try:
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()
except requests.RequestException as e:
    print(f"Error fetching data for {player_name} (ID: {player_id}): {{e}}")
    exit(1)

# Requested splits categories
requested_splits = [
    "Overall", "All Splits", "Breakdown", "vs. Left", "vs. Right", "Home", "Away",
    "Day", "Night", "March", "April", "May", "Last 7 Days", "Last 15 Days", "Last 30 Days",
    "vs. ARI", "vs. CHW", "vs. LAD", "vs. MIA", "vs. MIL", "vs. NYM", "vs. OAK",
    "vs. PHI", "vs. PIT", "vs. SD", "vs. SF", "vs. TEX",
    "American Family Field", "Chase Field", "Citi Field", "Dodger Stadium",
    "PETCO Park", "PNC Park", "Wrigley Field",
    "As LF", "As RF", "As DH",
    "Count 0-0", "Count 0-1", "Count 0-2", "Count 1-0", "Count 1-1", "Count 1-2",
    "Count 2-0", "Count 2-1", "Count 2-2", "Count 3-0", "Count 3-1", "Count 3-2",
    "Batting #2", "Batting #3",
    "None On", "Runners On", "Scoring Position", "Bases Loaded", "Lead Off Inning",
    "Scoring Position, 2 out"
]

# Extract stat names and labels
stat_names = data.get("names", [])
stat_labels = data.get("labels", [])
if not stat_names or not stat_labels:
    print("No stat names or labels found in the API response.")
    exit(1)

# Create mapping of stat names to labels
stat_mapping = dict(zip(stat_names, stat_labels))

# Prepare data for DataFrame
rows = []
split_categories = data.get("splitCategories", [])
if not split_categories:
    print("No split categories found in the API response.")
    exit(1)

# Process each split category
for category in split_categories:
    category_name = category.get("displayName", "Unknown")
    category_internal_name = category.get("name", "Unknown")
    for split in category.get("splits", []):
        split_name = split.get("displayName", "Unknown")
        split_abbreviation = split.get("abbreviation", split_name)
        stats = split.get("stats", [])
        if stats and split_name in requested_splits:
            row = {{"Category": category_name, "Split": split_name, "Abbreviation": split_abbreviation}}
            for i, value in enumerate(stats):
                if i < len(stat_names):
                    stat_label = stat_mapping.get(stat_names[i], stat_names[i])
                    row[stat_label] = value
            rows.append(row)

# Check for Overall/All Splits specifically
for category in split_categories:
    if category.get("name") == "split":
        for split in category.get("splits", []):
            if split.get("displayName") == "All Splits":
                split_name = "Overall"  # Map to requested "Overall"
                split_abbreviation = split.get("abbreviation", "Total")
                stats = split.get("stats", [])
                if stats:
                    row = {{"Category": "Overall", "Split": "Overall", "Abbreviation": split_abbreviation}}
                    for i, value in enumerate(stats):
                        if i < len(stat_names):
                            stat_label = stat_mapping.get(stat_names[i], stat_names[i])
                            row[stat_label] = value
                    rows.append(row)
                break

# Note unavailable splits
available_splits = {{row["Split"] for row in rows}}
unavailable_splits = [s for s in requested_splits if s not in available_splits and s not in ["All Splits", "Breakdown"]]
if unavailable_splits:
    print("\\nNote: The following splits are not available in the API response:")
    for split in unavailable_splits:
        print(f"- {{split}}")

# Create DataFrame
df = pd.DataFrame(rows)
if df.empty:
    print("No matching splits data found.")
    exit(1)

# Reorder columns
desired_columns = [
    "Category", "Split", "Abbreviation",
    "AB", "R", "H", "2B", "3B", "HR", "RBI", "BB", "HBP", "SO", "SB", "CS",
    "AVG", "OBP", "SLG", "OPS"
]
columns = [col for col in desired_columns if col in df.columns]
df = df[columns]

# Convert numeric columns to appropriate types
numeric_columns = ["AB", "R", "H", "2B", "3B", "HR", "RBI", "BB", "HBP", "SO", "SB", "CS"]
for col in numeric_columns:
    if col in df:
        df[col] = pd.to_numeric(df[col], errors="coerce")
percentage_columns = ["AVG", "OBP", "SLG", "OPS"]
for col in percentage_columns:
    if col in df:
        df[col] = df[col].astype(str)  # Keep as string to preserve formatting

# Define output directory and file
output_dir = "{base_dir}/{team}/{player_name_dir}"
os.makedirs(output_dir, exist_ok=True)
output_file = os.path.join(output_dir, f"{player_name_dir}_splits_2025_{{datetime.now().strftime('%Y%m%d')}}.csv")

# Save to CSV
df.to_csv(output_file, index=False)
print(f"\\nSplits data saved to {{output_file}}")

# Print formatted table
print(f"\\n{player_name} 2025 Splits Data:")
print(df.to_string(index=False))
'''

    # Template for player_stats.py
    stats_template = '''import requests
import pandas as pd
from datetime import datetime
import os
from bs4 import BeautifulSoup

player_id = "{player_id}"
player_name = "{player_name}"
player_name_slug = "{player_name_slug}"

# URL for stats
url = f"https://www.espn.com/mlb/player/stats/_/id/{player_id}/{player_name_slug}"

# Make the web request
headers = {{
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
}}
try:
    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status()
except requests.RequestException as e:
    print(f"Error fetching stats for {player_name} (ID: {player_id}): {{e}}")
    exit(1)

# Parse HTML
soup = BeautifulSoup(response.text, "html.parser")
tables = soup.find_all("table")
if not tables:
    print(f"No stats tables found for {player_name}")
    exit(1)

# Extract stats
rows = []
for table in tables:
    table_rows = table.find_all("tr")[1:]  # Skip header
    for row in table_rows:
        cols = row.find_all("td")
        row_data = [col.text.strip() for col in cols if col.text.strip()]
        if row_data and len(row_data) >= 2:  # Ensure at least SEASON and TEAM
            rows.append(row_data)

# Create DataFrame
columns = ["SEASON", "TEAM", "G", "AB", "R", "H", "2B", "3B", "HR", "RBI", "BB", "SO", "SB", "CS", "AVG", "OBP", "SLG", "OPS"]
df = pd.DataFrame(rows, columns=columns[:len(rows[0])])
if df.empty:
    print(f"No stats data found for {player_name}")
    exit(1)

# Convert numeric columns
numeric_columns = ["G", "AB", "R", "H", "2B", "3B", "HR", "RBI", "BB", "SO", "SB", "CS"]
for col in numeric_columns:
    if col in df:
        df[col] = pd.to_numeric(df[col], errors="coerce")
percentage_columns = ["AVG", "OBP", "SLG", "OPS"]
for col in percentage_columns:
    if col in df:
        df[col] = df[col].astype(str)

# Define output directory and file
output_dir = "{base_dir}/{team}/{player_name_dir}"
os.makedirs(output_dir, exist_ok=True)
output_file = os.path.join(output_dir, f"{player_name_dir}_stats_2025_{{datetime.now().strftime('%Y%m%d')}}.csv")

# Save to CSV
df.to_csv(output_file, index=False)
print(f"\\nStats data saved to {{output_file}}")

# Print formatted table
print(f"\\n{player_name} 2025 Stats Data:")
print(df.to_string(index=False))
'''

    # Template for player_batvspitch.py
    batvspitch_template = '''import requests
import pandas as pd
from datetime import datetime
import os
from bs4 import BeautifulSoup

player_id = "{player_id}"
player_name = "{player_name}"
team_id = "{team_id}"

# URL for bat vs pitch
url = f"https://www.espn.com/mlb/player/batvspitch/_/id/{player_id}/teamId/{team_id}"

# Make the web request
headers = {{
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
}}
try:
    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status()
except requests.RequestException as e:
    print(f"Error fetching bat vs pitch for {player_name} (ID: {player_id}): {{e}}")
    exit(1)

# Parse HTML
soup = BeautifulSoup(response.text, "html.parser")
tables = soup.find_all("div", class_="ResponsiveTable")
if not tables:
    print(f"No bat vs pitch tables found for {player_name}")
    exit(1)

# Extract stats
rows = []
for table in tables:
    tbody = table.find("tbody")
    if not tbody:
        continue
    table_rows = tbody.find_all("tr")
    for row in table_rows:
        cols = row.find_all("td")
        if not cols or len(cols) <= 1:
            continue
        row_data = [col.text.strip() for col in cols]
        if row_data[0].lower() == "totals":
            continue
        rows.append(row_data)

# Create DataFrame
columns = ["PITCHER", "AB", "H", "2B", "3B", "HR", "RBI", "BB", "SO", "AVG", "OBP", "SLG", "OPS"]
df = pd.DataFrame(rows, columns=columns[:len(rows[0])])
if df.empty:
    print(f"No bat vs pitch data found for {player_name}")
    exit(1)

# Convert numeric columns
numeric_columns = ["AB", "H", "2B", "3B", "HR", "RBI", "BB", "SO"]
for col in numeric_columns:
    if col in df:
        df[col] = pd.to_numeric(df[col], errors="coerce")
percentage_columns = ["AVG", "OBP", "SLG", "OPS"]
for col in percentage_columns:
    if col in df:
        df[col] = df[col].astype(str)

# Define output directory and file
output_dir = "{base_dir}/{team}/{player_name_dir}"
os.makedirs(output_dir, exist_ok=True)
output_file = os.path.join(output_dir, f"{player_name_dir}_batvspitch_2025_{{datetime.now().strftime('%Y%m%d')}}.csv")

# Save to CSV
df.to_csv(output_file, index=False)
print(f"\\nBat vs Pitch data saved to {{output_file}}")

# Print formatted table
print(f"\\n{player_name} 2025 Bat vs Pitch Data:")
print(df.to_string(index=False))
'''

    # Template for player_gamelog.py
    gamelog_template = '''import requests
import json
import os
import csv
from datetime import datetime
from dateutil import parser
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

player_id = "{player_id}"
player_name = "{player_name}"
team_id = "{team_id}"
team_name = "{team_name}"
season = 2025

# Stat mapping
STAT_MAPPING = [
    ("AB", "At Bats"),
    ("R", "Runs"),
    ("H", "Hits"),
    ("2B", "Doubles"),
    ("3B", "Triples"),
    ("HR", "Home Runs"),
    ("RBI", "Runs Batted In"),
    ("BB", "Walks"),
    ("HBP", "Hit By Pitch"),
    ("SO", "Strikeouts"),
    ("SB", "Stolen Bases"),
    ("CS", "Caught Stealing"),
    ("AVG", "Batting Average"),
    ("OBP", "On Base Percentage"),
    ("SLG", "Slugging Percentage"),
    ("OPS", "OPS")
]

# API URL
url = f"https://site.web.api.espn.com/apis/common/v3/sports/baseball/mlb/athletes/{player_id}/gamelog?season={{season}}"

# Function to extract opponent information
def get_opponent_info(event):
    try:
        opponent_obj = event.get('opponent', {{}})
        opponent_name = opponent_obj.get('displayName', 'Unknown')
        return opponent_name
    except Exception as e:
        logger.error(f"Error extracting opponent for event {{event.get('id', 'Unknown')}}: {{e}}")
        return 'Unknown'

# Function to parse date
def parse_date(raw_date):
    if not raw_date:
        return 'N/A'
    try:
        return parser.parse(raw_date).strftime("%Y-%m-%d")
    except Exception as e:
        logger.error(f"Date parsing failed for {{raw_date}}: {{e}}")
        return 'N/A'

# Function to get game result
def get_game_result(event):
    try:
        home_score = event.get('homeTeamScore')
        away_score = event.get('awayTeamScore')
        home_team_id = event.get('homeTeamId')
        
        if home_score is not None and away_score is not None:
            if home_team_id == team_id:  # Team is home team
                result = 'W' if int(home_score) > int(away_score) else 'L'
                return f"{{result}} {{home_score}}-{{away_score}}"
            else:  # Team is away team
                result = 'W' if int(away_score) > int(home_score) else 'L'
                return f"{{result}} {{away_score}}-{{home_score}}"
        return 'N/A'
    except Exception as e:
        logger.error(f"Error extracting result for event {{event.get('id', 'Unknown')}}: {{e}}")
        return 'N/A'

# Fetch data from API
logger.info(f"Fetching gamelog data for {{player_name}} ID {{player_id}}, season {{season}}")
response = requests.get(url)
if response.status_code == 200:
    data = response.json()
    logger.info("Successfully fetched data from API")
    
    # Save raw API response for debugging
    output_dir = "{base_dir}/{team}/{player_name_dir}"
    os.makedirs(output_dir, exist_ok=True)
    with open(os.path.join(output_dir, f"raw_response_{{player_id}}_{{season}}.json"), 'w') as f:
        json.dump(data, f, indent=2)
else:
    logger.error(f"API request failed with status {{response.status_code}}")
    print(f"Error: {{response.status_code}}")
    exit()

# Store problematic games for debugging
problematic_games = {{}}

# Prepare CSV data
csv_headers = ["Season", "Month", "Date", "Teams", "Result"] + [stat[1] for stat in STAT_MAPPING]
csv_data = []

# Initialize season name
season_name = str(season)
season_display_name = season_name

# Check if seasonTypes exists
if 'seasonTypes' in data:
    for season_type in data.get('seasonTypes', []):
        season_display_name = season_type.get('displayName', season_name)
        
# Process game-by-game stats
print(f"\\n{{'='*60}}")
print(f"Season: {{season_display_name}}")
print(f"{{'='*60}}")

# First method: Check if we have events directly in the data
games_processed = False
events_dict = data.get('events', {{}})
if events_dict:
    games_processed = True
    for game_id, event in events_dict.items():
        # Extract game data
        game_date = parse_date(event.get('gameDate', 'N/A'))
        month = 'Unknown'
        if game_date != 'N/A':
            try:
                month = datetime.strptime(game_date, "%Y-%m-%d").strftime("%B")
            except ValueError:
                logger.warning(f"Could not parse month from date {{game_date}}")
        
        print(f"\\nMonth: {{month}}")
        print(f"{{'-'*40}}")
        
        # Get opponent
        opponent_name = get_opponent_info(event)
        
        # Extract home/away indicator
        at_vs = event.get('atVs', 'vs')
        
        # Full team matchup
        matchup = f"{{team_name}} {{at_vs}} {{opponent_name}}"
        
        # Extract result
        game_result = get_game_result(event)
        
        # Print relevant information
        print(f"Teams: {{matchup}}")
        print(f"Date: {{game_date}}")
        print(f"Result: {{game_result}}")
        
        # Get stats 
        stats = []
        if 'stats' in event:
            stats = event.get('stats', [])
        else:
            # Try to look for stats in the 'categories' structure
            event_id = event.get('id', game_id)
            if 'seasonTypes' in data:
                for season_type in data.get('seasonTypes', []):
                    for category in season_type.get('categories', []):
                        if category.get('type') == 'event':
                            for evt in category.get('events', []):
                                if evt.get('eventId') == event_id:
                                    stats = evt.get('stats', [])
                                    break
        
        # Create CSV row
        csv_row = {{
            "Season": season_display_name,
            "Month": month,
            "Date": game_date,
            "Teams": matchup,
            "Result": game_result
        }}
        
        # Add stats to the row
        for i, (abbrev, name) in enumerate(STAT_MAPPING):
            value = stats[i] if i < len(stats) else 'N/A'
            print(f"  {{name:<20}}: {{value}}")
            csv_row[name] = value
        
        # Log problematic games
        if opponent_name == "Unknown" or game_date == "N/A" or game_result == "N/A" or len(stats) == 0:
            problematic_games[game_id] = {{"event": event, "stats_found": len(stats) > 0}}
        
        csv_data.append(csv_row)
        print()

# Second method: If no events were processed, try the seasonTypes structure
if not games_processed and 'seasonTypes' in data:
    for season_type in data.get('seasonTypes', []):
        season_display_name = season_type.get('displayName', season_name)
        
        for category in season_type.get('categories', []):
            if category.get('type') == 'event':
                month = category.get('displayName', 'Unknown').capitalize()
                print(f"\\nMonth: {{month}}")
                print(f"{{'-'*40}}")
                
                for event in category.get('events', []):
                    game_id = event.get('eventId', 'Unknown')
                    
                    # Look for corresponding event in the events dictionary if it exists
                    event_details = data.get('events', {{}}).get(game_id, {{}})
                    
                    # Get opponent
                    opponent_name = 'Unknown'
                    if event_details:
                        opponent_name = get_opponent_info(event_details)
                    else:
                        opponent_name = get_opponent_info(event)
                    
                    # Extract home/away indicator
                    at_vs = event.get('atVs', event_details.get('atVs', 'vs'))
                    
                    # Full team matchup
                    matchup = f"{{team_name}} {{at_vs}} {{opponent_name}}"
                    
                    # Extract date
                    raw_date = event.get('gameDate', event_details.get('gameDate', 'N/A'))
                    game_date = parse_date(raw_date)
                    
                    # Extract result
                    game_result = 'N/A'
                    if event_details:
                        game_result = get_game_result(event_details)
                    else:
                        game_result = get_game_result(event)
                    
                    # Print relevant information
                    print(f"Teams: {{matchup}}")
                    print(f"Date: {{game_date}}")
                    print(f"Result: {{game_result}}")
                    
                    # Get stats
                    stats = event.get('stats', [])
                    
                    # Create CSV row
                    csv_row = {{
                        "Season": season_display_name,
                        "Month": month,
                        "Date": game_date,
                        "Teams": matchup,
                        "Result": game_result
                    }}
                    
                    # Add stats to the row
                    for i, (abbrev, name) in enumerate(STAT_MAPPING):
                        value = stats[i] if i < len(stats) else 'N/A'
                        print(f"  {{name:<20}}: {{value}}")
                        csv_row[name] = value
                    
                    # Log problematic games
                    if opponent_name == "Unknown" or game_date == "N/A" or game_result == "N/A":
                        problematic_games[game_id] = {{"event": event, "stats_found": len(stats) > 0}}
                    
                    csv_data.append(csv_row)
                    print()

# Process season summary stats
summary_stats = []
if 'summary' in data and 'stats' in data['summary']:
    summary_stats = data['summary'].get('stats', [])
elif 'seasonTypes' in data:
    for season_type in data.get('seasonTypes', []):
        summary = data.get('summary', {{}}).get('stats', [])
        for stat_group in summary:
            if stat_group.get('type') == 'total':
                summary_stats = stat_group.get('stats', [])
                break

if summary_stats:
    print(f"\\n{{'='*60}}")
    print("Season Totals")
    print(f"{{'='*60}}")
    
    csv_row = {{
        "Season": season_display_name,
        "Month": "Total",
        "Date": "N/A",
        "Teams": "Season Totals",
        "Result": "N/A"
    }}
    
    for i, (abbrev, name) in enumerate(STAT_MAPPING):
        value = summary_stats[i] if i < len(summary_stats) else 'N/A'
        print(f"  {{name:<20}}: {{value}}")
        csv_row[name] = value
    
    csv_data.append(csv_row)

# Write to CSV
output_file = os.path.join(output_dir, f"{player_name_dir}_gamelog.csv")
if csv_data:
    with open(output_file, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=csv_headers)
        writer.writeheader()
        for row in csv_data:
            writer.writerow(row)
    
    print(f"\\nCSV file saved to: {{output_file}}")
else:
    logger.warning("No data was processed. CSV was not created.")

# Save problematic games for debugging
debug_file = os.path.join(output_dir, f"debug_player_{{player_id}}_{{season}}.json")
if problematic_games:
    print(f"\\nFound {{len(problematic_games)}} games with missing or incomplete data.")
    print(f"Writing debug data to {{debug_file}}")
    with open(debug_file, 'w') as f:
        json.dump(problematic_games, f, indent=2)
'''

    for team, team_data in team_rosters.items():
        team_id = team_data["team_id"]
        team_name = team.replace("-", " ").title()
        players = team_data["players"]
        team_folder = os.path.join(BASE_DIR, team)
        for player in players:
            player_name = player["name"]
            player_id = player["id"]
            # Sanitize player name
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
                        team_name=team_name,
                        base_dir=BASE_DIR,
                        team=team,
                        player_name_dir=player_name_dir
                    )
                    script_path = os.path.join(player_folder, f"player_{script_type}.py")
                    with open(script_path, "w", encoding="utf-8") as f:
                        f.write(script_content)
                    logger.info(f"Created script: {script_path}")
                except (OSError, ValueError, KeyError) as e:
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
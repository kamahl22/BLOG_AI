import requests
import os
import csv
from bs4 import BeautifulSoup

# Base directory for MLB teams
BASE_DIR = "/Users/kamahl/BLOG_AI/database_espn/mlb/teams"
os.makedirs(BASE_DIR, exist_ok=True)

def fetch_team_rosters():
    """Fetch updated rosters for all MLB teams using team IDs."""
    team_rosters = {}
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    }
    
    for team_id in range(1, 31):  # MLB team IDs range from 1 to 30
        url = f"https://site.api.espn.com/apis/site/v2/sports/baseball/mlb/teams/{team_id}/roster"
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            print(f"Failed to fetch roster for team ID {team_id}: {response.status_code}")
            continue
        
        data = response.json()
        team_info = data.get("team", {})
        team_location = team_info.get("location", "").lower().replace(" ", "-")
        team_name = team_info.get("name", "").lower().replace(" ", "-")
        full_team_name = f"{team_location}-{team_name}"
        
        team_folder = os.path.join(BASE_DIR, full_team_name)
        os.makedirs(team_folder, exist_ok=True)
        
        players = data.get("athletes", [])
        player_list = []
        for player in players:
            player_id = player.get("id", "N/A")
            player_name = player.get("fullName", "N/A")
            if player_id != "N/A" and player_name != "N/A":
                player_list.append({"name": player_name, "id": player_id})
        
        team_rosters[full_team_name] = player_list
        print(f"Fetched roster for {full_team_name}: {len(player_list)} players")
        
        # Save roster to CSV
        roster_csv = os.path.join(team_folder, f"{full_team_name}_roster.csv")
        with open(roster_csv, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Player Name", "Player ID"])
            writer.writerows([[p["name"], p["id"]] for p in player_list])
    
    return team_rosters

def create_player_folders_and_scripts(team_rosters):
    """Create folders and scripts for each player."""
    # Splits script template
    splits_template = '''
import requests
import csv
import os
from bs4 import BeautifulSoup

player_id = "{player_id}"
player_name = "{player_name}"

def fetch_and_save_data():
    url = f"https://www.espn.com/mlb/player/splits/_/id/{player_id}/{player_name.lower().replace(' ', '-')}"
    
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
    
    expected_headers = ["OVERALL", "AB", "R", "H", "2B", "3B", "HR", "RBI", "BB", "HBP", "SO", "SB", "CS", "AVG", "OBP", "SLG", "OPS"]
    
    preset_splits = [
        "All Splits", 
        "BREAKDOWN", "vs. Left", "vs. Right", "Home", "Away", "Day", "Night",
        "DAY/MONTH", "March", "April", "May", "June", "July", "August", "September", "October", "Last 7 Days", "Last 15 Days", "Last 30 Days",
        "OPPONENT", "vs. ARI", "vs. ATL", "vs. BAL", "vs. BOS", "vs. CHC", "vs. CWS", "vs. CIN", "vs. CLE", "vs. COL", "vs. DET",
        "vs. HOU", "vs. KC", "vs. LAA", "vs. LAD", "vs. MIA", "vs. MIL", "vs. MIN", "vs. NYM", "vs. NYY", "vs. OAK",
        "vs. PHI", "vs. PIT", "vs. SD", "vs. SF", "vs. SEA", "vs. STL", "vs. TB", "vs. TEX", "vs. TOR", "vs. WSH",
        "STADIUM", "American Family Field", "Chase Field", "Citi Field", "Comerica Park", "Coors Field", "Dodger Stadium",
        "Fenway Park", "Globe Life Field", "Great American Ball Park", "Guaranteed Rate Field", "Kauffman Stadium",
        "loanDepot park", "Minute Maid Park", "Nationals Park", "Oracle Park", "PETCO Park", "PNC Park",
        "Progressive Field", "Rogers Centre", "Target Field", "T-Mobile Park", "Tropicana Field", "Truist Park",
        "Wrigley Field", "Yankee Stadium",
        "POSITION", "As LF", "As RF", "As DH", "As C", "As 1B", "As 2B", "As 3B", "As SS", "As CF",
        "COUNT", "Count 0-0", "Count 0-1", "Count 0-2", "Count 1-0", "Count 1-1", "Count 1-2",
        "Count 2-0", "Count 2-1", "Count 2-2", "Count 3-0", "Count 3-1", "Count 3-2",
        "BATTING ORDER", "Batting #1", "Batting #2", "Batting #3", "Batting #4", "Batting #5", "Batting #6", "Batting #7", "Batting #8", "Batting #9",
        "SITUATION", "None On", "Runners On", "Scoring Position", "Bases Loaded", "Lead Off Inning", "Scoring Position, 2 out"
    ]
    
    default_stats = ["0", "0.0", "0.0-0.0", "0.0", "0.0-0.0", "0.0", "0.0-0.0", "0.0", "0.0", "0.0", "0.0", "0.0", "0.0", "0.0", "0.0", "0.0", "0.0"]
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
    player_folder = os.path.join(base_directory, "{team_name}", "{player_name_dir}")
    os.makedirs(player_folder, exist_ok=True)
    
    csv_filename = os.path.join(player_folder, f"{{player_name.lower().replace(' ', '_')}}_splits.csv")
    with open(csv_filename, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(expected_headers)
        writer.writerows(player_data)
    
    print(f"CSV file saved: {{csv_filename}}")
    return expected_headers, player_data

def print_excel_style():
    headers, data = fetch_and_save_data()
    if not headers or not data:
        print("No headers or data to display.")
        return
    
    max_cols = len(headers)
    col_widths = [len(str(h)) for h in headers]
    
    for row in data:
        padded_row = row + [""] * (max_cols - len(row)) if len(row) < max_cols else row[:max_cols]
        for i, cell in enumerate(padded_row):
            col_widths[i] = max(col_widths[i], len(str(cell)))
    
    top_border = "┌" + "─".join("─" * (w + 2) for w in col_widths) + "┐"
    bottom_border = "└" + "─".join("─" * (w + 2) for w in col_widths) + "┘"
    separator = "├" + "─".join("─" * (w + 2) for w in col_widths) + "┤"
    
    print(top_border)
    header_row = "│ " + " │ ".join(h.center(w) for h, w in zip(headers, col_widths)) + " │"
    print(header_row)
    print(separator)
    
    for row in data:
        padded_row = row + [""] * (max_cols - len(row)) if len(row) < max_cols else row[:max_cols]
        data_row = "│ " + " │ ".join(str(cell).ljust(w) for cell, w in zip(padded_row, col_widths)) + " │"
        print(data_row)
    
    print(bottom_border)

if __name__ == "__main__":
    print_excel_style()
'''

    # Stats script template (corrected to fetch stats instead of splits)
    stats_template = '''
import requests
import csv
import os
from bs4 import BeautifulSoup

player_id = "{player_id}"
player_name = "{player_name}"

def fetch_and_save_data():
    url = f"https://www.espn.com/mlb/player/splits/_/id/{player_id}/{player_name.lower().replace(' ', '-')}"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    }
    response = requests.get(url, headers=headers)
    
    print(f"Status Code: {response.status_code}")
    if response.status_code != 200:
        print(f"Error: Unable to fetch data for {player_name} (ID: {player_id}) - Status Code {response.status_code}")
        return None, None
    
    soup = BeautifulSoup(response.text, "html.parser")
    tables = soup.find_all("table")
    print(f"Number of tables found: {len(tables)}")
    
    if not tables:
        print(f"No stats tables found for {player_name}. The page structure may have changed.")
        return None, None
    
    expected_headers = ["OVERALL", "AB", "R", "H", "2B", "3B", "HR", "RBI", "BB", "HBP", "SO", "SB", "CS", "AVG", "OBP", "SLG", "OPS"]
    
    preset_splits = preset_splits = [
    "All Splits", 
    #Breakdown
    "BREAKDOWN","vs. Left", "vs. Right", "Home", "Away", "Day", "Night",
    #Day/Month
    "DAY/MONTH","March", "April", "May", "June", "July", "August", "September", "October", "Last 7 Days", "Last 15 Days", "Last 30 Days",
    # Opponent (all 30 teams)
    "OPPONENT", "vs. ARI", "vs. ATL", "vs. BAL", "vs. BOS", "vs. CHC", "vs. CWS", "vs. CIN", "vs. CLE", "vs. COL", "vs. DET",
    "vs. HOU", "vs. KC", "vs. LAA", "vs. LAD", "vs. MIA", "vs. MIL", "vs. MIN", "vs. NYM", "vs. NYY", "vs. OAK",
    "vs. PHI", "vs. PIT", "vs. SD", "vs. SF", "vs. SEA", "vs. STL", "vs. TB", "vs. TEX", "vs. TOR", "vs. WSH",
    # Stadium (all 30 stadiums)
    "STADIUM", "American Family Field", "Chase Field", "Citi Field", "Comerica Park", "Coors Field", "Dodger Stadium",
    "Fenway Park", "Globe Life Field", "Great American Ball Park", "Guaranteed Rate Field", "Kauffman Stadium",
    "loanDepot park", "Minute Maid Park", "Nationals Park", "Oracle Park", "PETCO Park", "PNC Park",
    "Progressive Field", "Rogers Centre", "Target Field", "T-Mobile Park", "Tropicana Field", "Truist Park",
    "Wrigley Field", "Yankee Stadium",
    #Position
    "POSITION", "As LF", "As RF", "As DH", "As C", "As 1B", "As 2B", "As 3B", "As SS", "As CF",
    #COUNT
    "COUNT", "Count 0-0", "Count 0-1", "Count 0-2", "Count 1-0", "Count 1-1", "Count 1-2",
    "Count 2-0", "Count 2-1", "Count 2-2", "Count 3-0", "Count 3-1", "Count 3-2",
    #Batting Order
    "BATTING ORDER", "Batting #1", "Batting #2", "Batting #3", "Batting #4", "Batting #5", "Batting #6", "Batting #7", "Batting #8", "Batting #9",
    #SITUATION
    "SITUATION", "None On", "Runners On", "Scoring Position", "Bases Loaded", "Lead Off Inning", "Scoring Position, 2 out"
]
    
    default_stats = ["0", "0.0", "0.0-0.0", "0.0", "0.0-0.0", "0.0", "0.0-0.0", "0.0", "0.0", "0.0", "0.0", "0.0", "0.0", "0.0", "0.0", "0.0", "0.0"]
    player_data_dict = {split: default_stats.copy() for split in preset_splits}
    
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
            print(f"Split found ({len(splits)-1}): ['{row_data[0]}']")
        elif len(row_data) > 1 and row_data[0].isdigit():
            stats_rows.append(row_data)
            print(f"Stats found ({len(stats_rows)-1}): {row_data}")
        else:
            print(f"Subheader: {row_data}")
        print()
    
    for idx, split in enumerate(splits):
        if idx < len(stats_rows):
            stats = stats_rows[idx][:len(expected_headers)-1] + ["N/A" for _ in range(len(stats_rows[idx]), len(expected_headers)-1)] if len(stats_rows[idx]) < len(expected_headers)-1 else stats_rows[idx][:len(expected_headers)-1]
            player_data_dict[split] = stats
            print(f"Paired: ['{split}'] with {stats}")
            print()
    
    player_data = [[split] + player_data_dict[split] for split in preset_splits]
    
    if not player_data:
        print(f"No player splits data found for {player_name}.")
        return None, None
    
    base_directory = "/Users/kamahl/BLOG_AI/database/espn/mlb/teams/chicago_cubs/player/player/{player_name}"
    player_folder = os.path.join(base_directory, "chicago-cubs", "{player_name}")
    os.makedirs(player_folder, exist_ok=True)
    
    csv_filename = os.path.join(player_folder, f"{player_name.lower().replace(' ', '_')}_splits.csv")
    with open(csv_filename, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(expected_headers)
        writer.writerows(player_data)
    
    print(f"CSV file saved: {csv_filename}")
    return expected_headers, player_data

def print_excel_style():
    headers, data = fetch_and_save_data()
    if not headers or not data:
        print("No headers or data to display.")
        return
    
    max_cols = len(headers)
    col_widths = [len(str(h)) for h in headers]
    
    for row in data:
        padded_row = row + [""] * (max_cols - len(row)) if len(row) < max_cols else row[:max_cols]
        for i, cell in enumerate(padded_row):
            col_widths[i] = max(col_widths[i], len(str(cell)))
    
    top_border = "┌" + "─".join("─" * (w + 2) for w in col_widths) + "┐"
    bottom_border = "└" + "─".join("─" * (w + 2) for w in col_widths) + "┘"
    separator = "├" + "─".join("─" * (w + 2) for w in col_widths) + "┤"
    
    print(top_border)
    header_row = "│ " + " │ ".join(h.center(w) for h, w in zip(headers, col_widths)) + " │"
    print(header_row)
    print(separator)
    
    for row in data:
        padded_row = row + [""] * (max_cols - len(row)) if len(row) < max_cols else row[:max_cols]
        data_row = "│ " + " │ ".join(str(cell).ljust(w) for cell, w in zip(padded_row, col_widths)) + " │"
        print(data_row)
    
    print(bottom_border)

if __name__ == "__main__":
    print_excel_style()
'''

    # Batter vs Pitcher script template
    batter_vs_pitcher_template = '''
import requests
import csv
import os
import re
from bs4 import BeautifulSoup

player_id = "{player_id}"
player_name = "{player_name}"

mlb_teams = {{
    "ARI": 29, "ATL": 15, "BAL": 1, "BOS": 2, "CHC": 16, "CWS": 4, "CIN": 17, "CLE": 5, "COL": 27, "DET": 6,
    "HOU": 18, "KC": 7, "LAA": 3, "LAD": 19, "MIA": 28, "MIL": 8, "MIN": 9, "NYM": 21, "NYY": 10, "OAK": 11,
    "PHI": 22, "PIT": 23, "SD": 25, "SF": 26, "SEA": 12, "STL": 24, "TB": 30, "TEX": 13, "TOR": 14, "WSH": 20
}}

def fetch_batvspitch_data(team_id, team_name):
    url = f"https://www.espn.com/mlb/player/batvspitch/_/id/{{player_id}}/teamId/{{team_id}}"
    headers = {{
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    }}
    
    print(f"Fetching Career Bat vs Pitch data for {{player_name}} (ID: {{player_id}}) vs {{team_name}} (teamId: {{team_id}}) from {{url}}")
    try:
        response = requests.get(url, headers=headers, timeout=10)
        print(f"Status Code for {{team_name}}: {{response.status_code}}")
        if response.status_code != 200:
            print(f"Error: Unable to fetch data for {{player_name}} vs {{team_name}} - Status Code {{response.status_code}}")
            return None
        return response.text
    except requests.RequestException as e:
        print(f"Request failed for {{team_name}}: {{e}}")
        return None

def extract_stats_headers(table):
    headers = []
    thead = table.find("thead")
    if thead:
        header_row = thead.find("tr")
        if header_row:
            header_cells = header_row.find_all("th")
            headers = [cell.text.strip() for cell in header_cells[1:] if cell.text.strip()]
    return headers

def parse_batvspitch_data(html_content, team_name):
    if not html_content:
        print(f"No HTML content to parse for {{team_name}}.")
        return None, None

    soup = BeautifulSoup(html_content, "html.parser")
    tables = soup.find_all("div", class_="ResponsiveTable")
    if not tables:
        print(f"No stats tables found for {{team_name}}. The page structure may have changed.")
        return None, None

    player_stats = {{}}
    stats_headers = []

    for i, table in enumerate(tables):
        print(f"Processing table {{i}} for {{team_name}}")
        table_scroll = table.find("div", class_="Table__Scroller")
        if not table_scroll:
            print(f"No scroller found in table {{i}} for {{team_name}}")
            continue

        if not stats_headers:
            stats_headers = extract_stats_headers(table_scroll)
            if not stats_headers:
                print(f"No stats headers found for {{team_name}} in table {{i}}. Using default headers.")
                stats_headers = ["AB", "H", "2B", "3B", "HR", "RBI", "BB", "K", "AVG", "OBP", "SLG", "OPS"]
            print(f"Found stats headers for {{team_name}} in table {{i}}: {{stats_headers}}")

        tbody = table_scroll.find("tbody")
        if not tbody:
            print(f"No tbody found in table {{i}} for {{team_name}}")
            continue

        current_category = team_name.upper()
        if current_category not in player_stats:
            player_stats[current_category] = {{}}

        rows = tbody.find_all("tr")
        for row in rows:
            cells = row.find_all("td")
            if not cells or len(cells) <= 1:
                continue

            first_cell_text = cells[0].text.strip()
            if not first_cell_text or first_cell_text == "Totals":
                print(f"Skipping row for {{team_name}}: {{first_cell_text}}")
                continue

            stats = [cell.text.strip() for cell in cells[1:]]
            is_valid_pitcher_row = len(stats) >= len(stats_headers) - 4 and \
                                   all(stat in ['', '-', '0'] or re.match(r'^\\d*\\.?\\d+$', stat) for stat in stats[:-4]) and \
                                   all(stat in ['-', '.000'] or re.match(r'^\\d*\\.?\\d+$', stat) for stat in stats[-4:])

            if is_valid_pitcher_row:
                pitcher_name = first_cell_text
                padded_stats = stats[:len(stats_headers)]
                if len(padded_stats) < len(stats_headers):
                    padded_stats += ["0"] * (len(stats_headers) - len(padded_stats))
                player_stats[current_category][pitcher_name] = padded_stats
                print(f"Added pitcher {{pitcher_name}} for {{team_name}} with stats: {{padded_stats}}")

    if not player_stats:
        print(f"No Bat vs Pitch stats found for {{team_name}}.")
        return None, stats_headers

    return player_stats, stats_headers

def format_and_save_csv():
    base_directory = "{base_dir}"
    player_folder = os.path.join(base_directory, "{team_name}", "{player_name_dir}")
    os.makedirs(player_folder, exist_ok=True)
    
    csv_filename = os.path.join(player_folder, f"{{player_name.lower().replace(' ', '_')}}_batvspitch.csv")
    
    csv_data = [["Team", "Pitcher"] + stats_headers]
    
    for team in sorted(all_player_stats.keys()):
        csv_data.append([team, ""] + [""] * len(stats_headers))
        for pitcher, stats in sorted(all_player_stats[team].items()):
            padded_stats = stats + [""] * (len(stats_headers) - len(stats))
            csv_data.append(["", pitcher] + padded_stats)

    with open(csv_filename, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerows(csv_data)
    
    print(f"CSV file saved: {{csv_filename}}")
    return csv_data

def main():
    all_player_stats = {{}}
    stats_headers = None

    for team_name, team_id in mlb_teams.items():
        html_content = fetch_batvspitch_data(team_id, team_name)
        if not html_content:
            print(f"No data fetched for {{team_name}}, initializing empty stats.")
            all_player_stats[team_name.upper()] = {{}}
            continue
        
        player_stats, fetched_headers = parse_batvspitch_data(html_content, team_name)
        if not player_stats:
            print(f"No valid pitcher stats parsed for {{team_name}}, initializing empty stats.")
            all_player_stats[team_name.upper()] = {{}}
            continue

        if stats_headers is None and fetched_headers:
            stats_headers = fetched_headers

        if stats_headers is None:
            stats_headers = ["AB", "H", "2B", "3B", "HR", "RBI", "BB", "K", "AVG", "OBP", "SLG", "OPS"]

        all_player_stats.update(player_stats)

    for team_name in mlb_teams.keys():
        if team_name.upper() not in all_player_stats:
            all_player_stats[team_name.upper()] = {{}}

    print(f"\\nFound Career Bat vs Pitch data for {{len(all_player_stats)}} teams:")
    total_pitchers = 0
    for team, pitchers in all_player_stats.items():
        print(f"  - {{team}}: {{len(pitchers)}} pitchers")
        total_pitchers += len(pitchers)
    
    csv_data = format_and_save_csv()
    
    print(f"\\nTotal teams: {{len(all_player_stats)}}")
    print(f"Total pitchers faced: {{total_pitchers}}")
    print(f"Stats columns: {{', '.join(stats_headers)}}")

if __name__ == "__main__":
    main()
'''

    # Gamelog script template
    gamelog_template = '''
import requests
import csv
import os
from bs4 import BeautifulSoup

player_id = "{player_id}"
player_name = "{player_name}"

def fetch_and_save_gamelog():
    url = f"https://www.espn.com/mlb/player/gamelog/_/id/{player_id}/{player_name.lower().replace(' ', '-')}"
    
    headers = {{
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    }}
    response = requests.get(url, headers=headers)
    
    print(f"Status Code: {{response.status_code}}")
    if response.status_code != 200:
        print(f"Error: Unable to fetch game log for {{player_name}} (ID: {{player_id}}) - Status Code {{response.status_code}}")
        return None, None
    
    soup = BeautifulSoup(response.text, "html.parser")
    tables = soup.find_all("table", class_="Table")
    
    print(f"Number of tables found: {{len(tables)}}")
    if not tables:
        print(f"No game log tables found for {{player_name}}. Dumping page snippet for debugging:")
        print(soup.prettify()[:1000])
        return None, None
    
    expected_headers = ["Date", "OPP", "Result", "AB", "R", "H", "2B", "3B", "HR", "RBI", "BB", "HBP", "SO", "SB", "CS", "AVG", "OBP", "SLG", "OPS"]
    
    game_data = []
    
    for table in tables:
        prev_sibling = table.find_previous_sibling("div", class_="Table__Title")
        season_label = prev_sibling.text.strip() if prev_sibling else "Unknown"
        print(f"Processing table with title: '{{season_label}}'")
        
        rows = table.find_all("tr")[1:]
        print(f"Number of rows in table: {{len(rows)}}")
        
        for row in rows:
            cols = row.find_all("td")
            if len(cols) < 2:
                print(f"Skipping row with insufficient columns: {{[col.text.strip() for col in cols]}}")
                continue
            
            date = cols[0].text.strip()
            if not any(day in date.lower() for day in ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]):
                print(f"Skipping summary row: {{date}}")
                continue
            
            opponent = cols[1].text.strip()
            raw_result = cols[2].text.strip()
            if len(raw_result) > 1 and raw_result[0] in {{"W", "L", "T"}} and raw_result[1].isdigit():
                result = raw_result[0] + " " + raw_result[1:]
            else:
                result = raw_result
            stats = [col.text.strip() for col in cols[3:]]
            
            print(f"Raw row data: {{[date, opponent, result] + stats}}")
            
            if len(stats) < len(expected_headers) - 3:
                stats.extend(["N/A"] * (len(expected_headers) - 3 - len(stats)))
            game_row = [date, opponent, result] + stats[:16]
            game_data.append(game_row)
    
    if not game_data:
        print(f"No game log data found for {{player_name}} in the season.")
        return None, None
    
    print(f"Collected {{len(game_data)}} games for {{player_name}}")
    
    base_directory = "{base_dir}"
    player_folder = os.path.join(base_directory, "{team_name}", "{player_name_dir}")
    os.makedirs(player_folder, exist_ok=True)
    csv_filename = os.path.join(player_folder, f"{{player_name.lower().replace(' ', '_')}}_gamelog.csv")
    
    with open(csv_filename, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(expected_headers)
        writer.writerows(game_data)
    
    print(f"CSV file saved: {{csv_filename}}")
    return expected_headers, game_data

def print_excel_style():
    headers, data = fetch_and_save_gamelog()
    if not headers or not data:
        print("No headers or data to display.")
        return
    
    col_widths = [len(str(h)) for h in headers]
    for row in data:
        for i, cell in enumerate(row):
            col_widths[i] = max(col_widths[i], len(str(cell)))
    
    top_border = "┌" + "─".join("─" * (w + 2) for w in col_widths) + "┐"
    bottom_border = "└" + "─".join("─" * (w + 2) for w in col_widths) + "┘"
    separator = "├" + "─".join("─" * (w + 2) for w in col_widths) + "┤"
    
    print(top_border)
    header_row = "│ " + " │ ".join(h.center(w) for h, w in zip(headers, col_widths)) + " │"
    print(header_row)
    print(separator)
    
    for row in data:
        data_row = "│ " + " │ ".join(str(cell).ljust(w) for cell, w in zip(row, col_widths)) + " │"
        print(data_row)
    
    print(bottom_border)

if __name__ == "__main__":
    print_excel_style()
'''

    for team, players in team_rosters.items():
        team_folder = os.path.join(BASE_DIR, team)
        for player in players:
            player_name = player["name"]
            player_id = player["id"]
            player_name_dir = player_name.lower().replace(" ", "_")
            player_folder = os.path.join(team_folder, player_name_dir)
            os.makedirs(player_folder, exist_ok=True)
            
            format_vars = {
                "player_id": player_id,
                "player_name": player_name,
                "base_dir": BASE_DIR,
                "team_name": team,
                "player_name_dir": player_name_dir
            }
            
            # Generate splits script
            splits_script = splits_template.format(**format_vars)
            splits_path = os.path.join(player_folder, f"{player_name_dir}_splits.py")
            with open(splits_path, "w", encoding="utf-8") as f:
                f.write(splits_script)
            
            # Generate stats script
            stats_script = stats_template.format(**format_vars)
            stats_path = os.path.join(player_folder, f"{player_name_dir}_stats.py")
            with open(stats_path, "w", encoding="utf-8") as f:
                f.write(stats_script)
            
            # Generate batter vs pitcher script
            batter_vs_pitcher_script = batter_vs_pitcher_template.format(**format_vars)
            batter_vs_pitcher_path = os.path.join(player_folder, f"{player_name_dir}_batter_vs_pitcher.py")
            with open(batter_vs_pitcher_path, "w", encoding="utf-8") as f:
                f.write(batter_vs_pitcher_script)
            
            # Generate gamelog script
            gamelog_script = gamelog_template.format(**format_vars)
            gamelog_path = os.path.join(player_folder, f"{player_name_dir}_gamelog.py")
            with open(gamelog_path, "w", encoding="utf-8") as f:
                f.write(gamelog_script)
            
            print(f"Created scripts for {player_name} in {player_folder}")

def main():
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
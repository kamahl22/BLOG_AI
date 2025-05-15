import requests
import csv
import os
import re
from bs4 import BeautifulSoup

# Dictionary of MLB teams and their ESPN team IDs
mlb_teams = {
    "ARI": 29, "ATL": 15, "BAL": 1, "BOS": 2, "CHC": 16, "CWS": 4, "CIN": 17, "CLE": 5, "COL": 27, "DET": 6,
    "HOU": 18, "KC": 7, "LAA": 3, "LAD": 19, "MIA": 28, "MIL": 8, "MIN": 9, "NYM": 21, "NYY": 10, "OAK": 11,
    "PHI": 22, "PIT": 23, "SD": 25, "SF": 26, "SEA": 12, "STL": 24, "TB": 30, "TEX": 13, "TOR": 14, "WSH": 20
}

def fetch_batvspitch_data(player_id, player_name, team_id, team_name):
    """Fetch the HTML content from the player's ESPN Bat vs Pitch page for a specific team."""
    url = f"https://www.espn.com/mlb/player/batvspitch/_/id/{player_id}/teamId/{team_id}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    }
    
    print(f"Fetching Career Bat vs Pitch data for {player_name} (ID: {player_id}) vs {team_name} (teamId: {team_id}) from {url}")
    try:
        response = requests.get(url, headers=headers, timeout=10)
        print(f"Status Code for {team_name}: {response.status_code}")
        if response.status_code != 200:
            print(f"Error: Unable to fetch data for {player_name} vs {team_name} - Status Code {response.status_code}")
            return None
        return response.text
    except requests.RequestException as e:
        print(f"Request failed for {team_name}: {e}")
        return None

def extract_stats_headers(table):
    """Extract column headers from a stats table."""
    headers = []
    thead = table.find("thead")
    if thead:
        header_row = thead.find("tr")
        if header_row:
            header_cells = header_row.find_all("th")
            headers = [cell.text.strip() for cell in header_cells[1:] if cell.text.strip()]  # Skip first column (Pitcher)
    return headers

def parse_batvspitch_data(html_content, team_name):
    """Parse the Bat vs Pitch data from the ESPN page HTML content."""
    if not html_content:
        print(f"No HTML content to parse for {team_name}.")
        return None, None

    soup = BeautifulSoup(html_content, "html.parser")
    
    tables = soup.find_all("div", class_="ResponsiveTable")
    if not tables:
        print(f"No stats tables found for {team_name}. The page structure may have changed.")
        return None, None

    player_stats = {}
    stats_headers = []

    for i, table in enumerate(tables):
        print(f"Processing table {i} for {team_name}")
        # Find the table scroller
        table_scroll = table.find("div", class_="Table__Scroller")
        if not table_scroll:
            print(f"No scroller found in table {i} for {team_name}")
            continue

        # Extract headers
        if not stats_headers:
            stats_headers = extract_stats_headers(table_scroll)
            if not stats_headers:
                print(f"No stats headers found for {team_name} in table {i}. Using default headers.")
                stats_headers = ["AB", "H", "2B", "3B", "HR", "RBI", "BB", "K", "AVG", "OBP", "SLG", "OPS"]
            print(f"Found stats headers for {team_name} in table {i}: {stats_headers}")

        # Find the table body
        tbody = table_scroll.find("tbody")
        if not tbody:
            print(f"No tbody found in table {i} for {team_name}")
            continue

        current_category = team_name.upper()
        if current_category not in player_stats:
            player_stats[current_category] = {}

        rows = tbody.find_all("tr")
        for row in rows:
            cells = row.find_all("td")
            if not cells or len(cells) <= 1:
                continue

            first_cell_text = cells[0].text.strip()
            if not first_cell_text or first_cell_text == "Totals":
                print(f"Skipping row for {team_name}: {first_cell_text}")
                continue

            # Debug: Print raw row data
            print(f"Processing row for {team_name}: {first_cell_text} | {', '.join(cell.text.strip() for cell in cells[1:])}")

            # Loosen validation to capture all pitcher rows
            stats = [cell.text.strip() for cell in cells[1:]]
            is_valid_pitcher_row = len(stats) >= len(stats_headers) - 4 and \
                                   all(stat in ['', '-', '0'] or re.match(r'^\d*\.?\d+$', stat) for stat in stats[:-4]) and \
                                   all(stat in ['-', '.000'] or re.match(r'^\d*\.?\d+$', stat) for stat in stats[-4:])

            if is_valid_pitcher_row:
                pitcher_name = first_cell_text
                padded_stats = stats[:len(stats_headers)]
                if len(padded_stats) < len(stats_headers):
                    padded_stats += ["0"] * (len(stats_headers) - len(padded_stats))
                player_stats[current_category][pitcher_name] = padded_stats
                print(f"Added pitcher {pitcher_name} for {team_name} with stats: {padded_stats}")

    if not player_stats:
        print(f"No Bat vs Pitch stats found for {team_name}.")
        return None, stats_headers

    return player_stats, stats_headers

def format_and_save_csv(player_name, player_stats, stats_headers, base_directory):
    """Format and save the player stats to a hierarchical CSV file."""
    player_directory = base_directory
    os.makedirs(player_directory, exist_ok=True)
    
    csv_filename = os.path.join(player_directory, f"{player_name.lower().replace(' ', '_')}_batvspitch.csv")
    
    csv_data = [["Team", "Pitcher"] + stats_headers]
    
    # Sort teams alphabetically
    for team in sorted(player_stats.keys()):
        csv_data.append([team, ""] + [""] * len(stats_headers))
        for pitcher, stats in sorted(player_stats[team].items()):
            padded_stats = stats + [""] * (len(stats_headers) - len(stats))
            csv_data.append(["", pitcher] + padded_stats)

    with open(csv_filename, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerows(csv_data)
    
    print(f"✅ CSV file saved: {csv_filename}")
    return csv_data

def print_table(data):
    """Print formatted table with the player stats."""
    if not data or len(data) <= 1:
        print("No data to display")
        return
        
    max_cols = max(len(row) for row in data)
    col_widths = [max(len(str(row[i])) if i < len(row) else 0 for row in data) for i in range(max_cols)]
    
    top_border = "┌" + "┬".join("─" * (w + 2) for w in col_widths) + "┐"
    header_separator = "├" + "┼".join("─" * (w + 2) for w in col_widths) + "┤"
    category_separator = "├" + "┼".join("─" * (w + 2) for w in col_widths) + "┤"
    bottom_border = "└" + "┴".join("─" * (w + 2) for w in col_widths) + "┘"
    
    print(top_border)
    header_cells = [str(data[0][i]).center(col_widths[i]) for i in range(len(data[0]))]
    print("│ " + " │ ".join(header_cells) + " │")
    print(header_separator)
    
    last_team = None
    for row in data[1:]:
        is_team_row = bool(row[0]) and not bool(row[1])
        if is_team_row and last_team:
            print(category_separator)
        last_team = row[0] if is_team_row else last_team
        
        formatted_cells = [str(cell).ljust(col_widths[i]) for i, cell in enumerate(row)]
        print("│ " + " │ ".join(formatted_cells) + " │")
    
    print(bottom_border)

def main(player_id, player_name, base_directory):
    """Main function to execute the scraping process for all teams."""
    all_player_stats = {}
    stats_headers = None

    # Iterate over all MLB teams
    for team_name, team_id in mlb_teams.items():
        html_content = fetch_batvspitch_data(player_id, player_name, team_id, team_name)
        if not html_content:
            print(f"No data fetched for {team_name}, initializing empty stats.")
            all_player_stats[team_name.upper()] = {}
            continue
        
        player_stats, fetched_headers = parse_batvspitch_data(html_content, team_name)
        if not player_stats:
            print(f"No valid pitcher stats parsed for {team_name}, initializing empty stats.")
            all_player_stats[team_name.upper()] = {}
            continue

        # Set headers from the first successful fetch
        if stats_headers is None and fetched_headers:
            stats_headers = fetched_headers

        # Use default headers if none fetched yet
        if stats_headers is None:
            stats_headers = ["AB", "H", "2B", "3B", "HR", "RBI", "BB", "K", "AVG", "OBP", "SLG", "OPS"]

        all_player_stats.update(player_stats)

    # Ensure all teams have entries
    for team_name in mlb_teams.keys():
        if team_name.upper() not in all_player_stats:
            all_player_stats[team_name.upper()] = {}

    print(f"\nFound Career Bat vs Pitch data for {len(all_player_stats)} teams:")
    total_pitchers = 0
    for team, pitchers in all_player_stats.items():
        print(f"  - {team}: {len(pitchers)} pitchers")
        total_pitchers += len(pitchers)
    
    csv_data = format_and_save_csv(player_name, all_player_stats, stats_headers, base_directory)
    
    print(f"\nCareer Bat vs Pitch for {player_name}")
    print_table(csv_data)
    
    print(f"\nTotal teams: {len(all_player_stats)}")
    print(f"Total pitchers faced: {total_pitchers}")
    print(f"Stats columns: {', '.join(stats_headers)}")
    print("Sample of parsed data (first 3 non-header rows):")
    for row in csv_data[1:4]:
        print(row)

if __name__ == "__main__":
    player_id = "4142424"  # Corrected ID for Seiya Suzuki
    player_name = "Seiya Suzuki"
    base_directory = "/Users/kamahl/BLOG_AI/database/espn/mlb/teams/chicago_cubs/player/player/seiya_suzuki"
    main(player_id, player_name, base_directory)
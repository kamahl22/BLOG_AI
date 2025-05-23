import requests
import csv
import os
from bs4 import BeautifulSoup

player_id = "4142424"
player_name = "Seiya Suzuki"

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
    
    base_directory = "/Users/kamahl/BLOG_AI/database/espn/mlb/teams/chicago_cubs/player/player/seiya_suzuki"
    player_folder = os.path.join(base_directory, "chicago-cubs", "seiya_suzuki")
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
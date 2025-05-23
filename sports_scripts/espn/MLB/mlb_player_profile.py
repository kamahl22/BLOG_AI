import requests
import pandas as pd
from datetime import datetime
import os

# API endpoints
gamelog_url = "https://site.web.api.espn.com/apis/common/v3/sports/baseball/mlb/athletes/4142424/statistics?season=2025"
splits_url = "https://site.web.api.espn.com/apis/common/v3/sports/baseball/mlb/athletes/4142424/splits?season=2025"

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

# Function to fetch JSON data
def fetch_json(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return None

# Fetch game log and splits data
gamelog_data = fetch_json(gamelog_url)
splits_data = fetch_json(splits_url)

# Process splits data
splits_rows = []
stat_mapping = {}
if splits_data:
    stat_names = splits_data.get("names", [])
    stat_labels = splits_data.get("labels", [])
    stat_mapping = dict(zip(stat_names, stat_labels))
    
    split_categories = splits_data.get("splitCategories", [])
    if not split_categories:
        print("No split categories found in splits API response.")
    else:
        for category in split_categories:
            category_name = category.get("displayName", "Unknown")
            category_internal_name = category.get("name", "Unknown")
            for split in category.get("splits", []):
                split_name = split.get("displayName", "Unknown")
                split_abbreviation = split.get("abbreviation", split_name)
                stats = split.get("stats", [])
                if stats and split_name in requested_splits:
                    row = {"Category": category_name, "Split": split_name, "Abbreviation": split_abbreviation}
                    for i, value in enumerate(stats):
                        if i < len(stat_names):
                            stat_label = stat_mapping.get(stat_names[i], stat_names[i])
                            row[stat_label] = value
                    splits_rows.append(row)
        
        # Handle Overall/All Splits
        for category in split_categories:
            if category.get("name") == "split":
                for split in category.get("splits", []):
                    if split.get("displayName") == "All Splits":
                        split_name = "Overall"
                        split_abbreviation = split.get("abbreviation", "Total")
                        stats = split.get("stats", [])
                        if stats:
                            row = {"Category": "Overall", "Split": "Overall", "Abbreviation": split_abbreviation}
                            for i, value in enumerate(stats):
                                if i < len(stat_names):
                                    stat_label = stat_mapping.get(stat_names[i], stat_names[i])
                                    row[stat_label] = value
                            splits_rows.append(row)
                        break
else:
    print("No splits data retrieved.")

# Process game log data
gamelog_rows = []
if gamelog_data:
    # Try common MLB gamelog structures
    dates = gamelog_data.get("dates", [])
    games = gamelog_data.get("games", [])  # Alternative structure
    entries = gamelog_data.get("entries", [])  # Another possible structure
    
    if dates:
        for date_entry in dates:
            date_games = date_entry.get("games", [])
            for game in date_games:
                stats = game.get("stats", {})
                opponent = game.get("opponent", {}).get("displayName", "Unknown")
                game_id = game.get("gameId", "Unknown")
                game_date = date_entry.get("date", "Unknown")
                if stats:
                    row = {
                        "GameDate": game_date,
                        "Opponent": opponent,
                        "GameID": game_id
                    }
                    for stat_name, stat_value in stats.items():
                        stat_label = stat_mapping.get(stat_name, stat_name)
                        row[stat_label] = stat_value
                    gamelog_rows.append(row)
    
    elif games:
        for game in games:
            stats = game.get("stats", {})
            opponent = game.get("opponent", {}).get("displayName", "Unknown")
            game_id = game.get("gameId", "Unknown")
            game_date = game.get("date", "Unknown")
            if stats:
                row = {
                    "GameDate": game_date,
                    "Opponent": opponent,
                    "GameID": game_id
                }
                for stat_name, stat_value in stats.items():
                    stat_label = stat_mapping.get(stat_name, stat_name)
                    row[stat_label] = stat_value
                gamelog_rows.append(row)
    
    elif entries:
        for entry in entries:
            game_info = entry.get("game", {})
            stats = entry.get("stats", {})
            if stats:
                row = {
                    "GameDate": game_info.get("date", "Unknown"),
                    "Opponent": game_info.get("opponent", {}).get("displayName", "Unknown"),
                    "GameID": game_info.get("id", "Unknown")
                }
                for stat_name, stat_value in stats.items():
                    stat_label = stat_mapping.get(stat_name, stat_name)
                    row[stat_label] = stat_value
                gamelog_rows.append(row)
    
    if not gamelog_rows:
        print("No game log entries found in API response.")
else:
    print("No game log data retrieved. Check endpoint or season parameter.")

# Note unavailable splits
available_splits = {row["Split"] for row in splits_rows}
unavailable_splits = [s for s in requested_splits if s not in available_splits and s not in ["All Splits", "Breakdown"]]
if unavailable_splits:
    print("\nNote: The following splits are not available in the splits API response:")
    for split in unavailable_splits:
        print(f"- {split}")

# Create DataFrames
splits_df = pd.DataFrame(splits_rows)
gamelog_df = pd.DataFrame(gamelog_rows)

# Define columns
desired_columns = [
    "Category", "Split", "Abbreviation",
    "AB", "R", "H", "2B", "3B", "HR", "RBI", "BB", "HBP", "SO", "SB", "CS",
    "AVG", "OBP", "SLG", "OPS"
]
gamelog_columns = [
    "GameDate", "Opponent", "GameID",
    "AB", "R", "H", "2B", "3B", "HR", "RBI", "BB", "HBP", "SO", "SB", "CS",
    "AVG", "OBP", "SLG", "OPS"
]

# Filter and reorder columns
if not splits_df.empty:
    splits_columns = [col for col in desired_columns if col in splits_df.columns]
    splits_df = splits_df[splits_columns]
    # Convert numeric and percentage columns
    numeric_columns = ["AB", "R", "H", "2B", "3B", "HR", "RBI", "BB", "HBP", "SO", "SB", "CS"]
    for col in numeric_columns:
        if col in splits_df:
            splits_df[col] = pd.to_numeric(splits_df[col], errors="coerce")
    percentage_columns = ["AVG", "OBP", "SLG", "OPS"]
    for col in percentage_columns:
        if col in splits_df:
            splits_df[col] = splits_df[col].astype(str)

if not gamelog_df.empty:
    gamelog_columns = [col for col in gamelog_columns if col in gamelog_df.columns]
    gamelog_df = gamelog_df[gamelog_columns]
    # Convert numeric and percentage columns
    for col in numeric_columns:
        if col in gamelog_df:
            gamelog_df[col] = pd.to_numeric(gamelog_df[col], errors="coerce")
    for col in percentage_columns:
        if col in gamelog_df:
            gamelog_df[col] = gamelog_df[col].astype(str)

# Define output directory and file
output_dir = "/Users/kamahl/BLOG_AI/sports/espn/mlb/chicago-cubs/seiya-suzuki"
os.makedirs(output_dir, exist_ok=True)
output_file = os.path.join(output_dir, f"seiya_suzuki_gamelog_splits_2025_{datetime.now().strftime('%Y%m%d')}.csv")

# Combine DataFrames for CSV
if not splits_df.empty and not gamelog_df.empty:
    combined_df = pd.concat([splits_df, gamelog_df], ignore_index=True, sort=False)
elif not splits_df.empty:
    combined_df = splits_df
elif not gamelog_df.empty:
    combined_df = gamelog_df
else:
    print("No data to save.")
    exit(1)

# Save to CSV
combined_df.to_csv(output_file, index=False)
print(f"\nData saved to {output_file}")

# Print formatted tables
if not splits_df.empty:
    print("\nSeiya Suzuki 2025 Splits Data:")
    print(splits_df.to_string(index=False))
if not gamelog_df.empty:
    print("\nSeiya Suzuki 2025 Game Log Data:")
    print(gamelog_df.to_string(index=False))

# Suggest alternatives if game log is empty
if not gamelog_rows:
    print("\nAlternative approaches to fetch game log data:")
    print("- Inspect ESPN player page (https://www.espn.com/mlb/player/gamelog/_/id/4142424) using Developer Tools to find the correct API call.")
    print("- Try alternative endpoint: https://sports.core.api.espn.com/v2/sports/baseball/leagues/mlb/seasons/2025/athletes/4142424/statisticslog")
    print("- Use Baseball-Reference (https://www.baseball-reference.com/players/s/suzukse01.shtml) for game logs.")
    print("- Use FanGraphs (https://www.fangraphs.com/players/seiya-suzuki/22821) for game-by-game data.")
    print("- Check MLB.com Statcast (https://baseballsavant.mlb.com/savant-player/seiya-suzuki-660294) for game-level stats.")
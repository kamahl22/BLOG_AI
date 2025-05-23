import requests
import pandas as pd
from datetime import datetime
import os

player_id = "32721"
player_name = "Gio Urshela"
player_name_slug = "gio-urshela"

# API endpoint for splits
url = "https://site.web.api.espn.com/apis/common/v3/sports/baseball/mlb/athletes/32721/splits?season=2025"

# Make the API call
try:
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()
except requests.RequestException as e:
    print(f"Error fetching data for Gio Urshela (ID: 32721): {e}")
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
            row = {"Category": category_name, "Split": split_name, "Abbreviation": split_abbreviation}
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
                    row = {"Category": "Overall", "Split": "Overall", "Abbreviation": split_abbreviation}
                    for i, value in enumerate(stats):
                        if i < len(stat_names):
                            stat_label = stat_mapping.get(stat_names[i], stat_names[i])
                            row[stat_label] = value
                    rows.append(row)
                break

# Note unavailable splits
available_splits = {row["Split"] for row in rows}
unavailable_splits = [s for s in requested_splits if s not in available_splits and s not in ["All Splits", "Breakdown"]]
if unavailable_splits:
    print("\nNote: The following splits are not available in the API response:")
    for split in unavailable_splits:
        print(f"- {split}")

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
output_dir = "/Users/kamahl/BLOG_AI/espn/mlb/athletics-athletics/gio_urshela"
os.makedirs(output_dir, exist_ok=True)
output_file = os.path.join(output_dir, f"gio_urshela_splits_2025_{datetime.now().strftime('%Y%m%d')}.csv")

# Save to CSV
df.to_csv(output_file, index=False)
print(f"\nSplits data saved to {output_file}")

# Print formatted table
print(f"\nGio Urshela 2025 Splits Data:")
print(df.to_string(index=False))

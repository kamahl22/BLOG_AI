import requests
import pandas as pd
from datetime import datetime
import os
from bs4 import BeautifulSoup

player_id = "40423"
player_name = "Gavin Lux"
player_name_slug = "gavin-lux"

# URL for stats
url = f"https://www.espn.com/mlb/player/stats/_/id/40423/gavin-lux"

# Make the web request
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
}
try:
    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status()
except requests.RequestException as e:
    print(f"Error fetching stats for Gavin Lux (ID: 40423): {e}")
    exit(1)

# Parse HTML
soup = BeautifulSoup(response.text, "html.parser")
tables = soup.find_all("table")
if not tables:
    print(f"No stats tables found for Gavin Lux")
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
    print(f"No stats data found for Gavin Lux")
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
output_dir = "/Users/kamahl/BLOG_AI/espn/mlb/cincinnati-reds/gavin_lux"
os.makedirs(output_dir, exist_ok=True)
output_file = os.path.join(output_dir, f"gavin_lux_stats_2025_{datetime.now().strftime('%Y%m%d')}.csv")

# Save to CSV
df.to_csv(output_file, index=False)
print(f"\nStats data saved to {output_file}")

# Print formatted table
print(f"\nGavin Lux 2025 Stats Data:")
print(df.to_string(index=False))

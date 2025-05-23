import requests
import pandas as pd
from datetime import datetime
import os
from bs4 import BeautifulSoup

player_id = "41233"
player_name = "Carlos Hernandez"
team_id = "22"

# URL for bat vs pitch
url = f"https://www.espn.com/mlb/player/batvspitch/_/id/41233/teamId/22"

# Make the web request
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
}
try:
    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status()
except requests.RequestException as e:
    print(f"Error fetching bat vs pitch for Carlos Hernandez (ID: 41233): {e}")
    exit(1)

# Parse HTML
soup = BeautifulSoup(response.text, "html.parser")
tables = soup.find_all("div", class_="ResponsiveTable")
if not tables:
    print(f"No bat vs pitch tables found for Carlos Hernandez")
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
    print(f"No bat vs pitch data found for Carlos Hernandez")
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
output_dir = "/Users/kamahl/BLOG_AI/espn/mlb/philadelphia-phillies/carlos_hernandez"
os.makedirs(output_dir, exist_ok=True)
output_file = os.path.join(output_dir, f"carlos_hernandez_batvspitch_2025_{datetime.now().strftime('%Y%m%d')}.csv")

# Save to CSV
df.to_csv(output_file, index=False)
print(f"\nBat vs Pitch data saved to {output_file}")

# Print formatted table
print(f"\nCarlos Hernandez 2025 Bat vs Pitch Data:")
print(df.to_string(index=False))

import requests
from bs4 import BeautifulSoup
import csv
import os

player_id = "N/A"
player_name = "Nicky Lopez"

def fetch_batter_vs_pitcher():
    url = f"https://www.espn.com/mlb/player/gamelog/_/id/{player_id}/{player_name.lower().replace(' ', '-')}"
    headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36"}
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"Error fetching batter vs pitcher for Nicky Lopez: {response.status_code}")
        return
    soup = BeautifulSoup(response.text, "html.parser")
    tables = soup.find_all("table")
    if not tables:
        print(f"No batter vs pitcher data found for Nicky Lopez")
        return
    with open(os.path.join("/Users/kamahl/BLOG_AI/database/espn/mlb/teams/chicago_cubs/player/player/nicky_lopez", "nicky_lopez_batter_vs_pitcher.csv"), "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Name", "Opponent", "Date", "Result"])
        for table in tables:
            for row in table.find_all("tr")[1:]:
                cols = row.find_all("td")
                if cols and len(cols) >= 4:
                    writer.writerow([player_name] + [col.text.strip() for col in cols[:4]])
    print(f"Saved batter vs pitcher for Nicky Lopez")

if __name__ == "__main__":
    fetch_batter_vs_pitcher()

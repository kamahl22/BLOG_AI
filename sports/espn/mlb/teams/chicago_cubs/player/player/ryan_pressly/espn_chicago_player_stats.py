import requests
from bs4 import BeautifulSoup
import csv
import os

player_id = "N/A"
player_name = "Ryan Pressly"

def fetch_player_stats():
    url = f"https://www.espn.com/mlb/player/stats/_/id/{player_id}/{player_name.lower().replace(' ', '-')}"
    headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36"}
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"Error fetching stats for Ryan Pressly: {response.status_code}")
        return
    soup = BeautifulSoup(response.text, "html.parser")
    tables = soup.find_all("table")
    if not tables:
        print(f"No stats tables found for Ryan Pressly")
        return
    with open(os.path.join("/Users/kamahl/BLOG_AI/database/espn/mlb/teams/chicago_cubs/player/player/ryan_pressly", "ryan_pressly_stats.csv"), "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Name", "GP", "IP", "W", "L", "ERA", "SO"])
        for table in tables:
            for row in table.find_all("tr")[1:]:
                cols = row.find_all("td")
                if cols:
                    writer.writerow([player_name] + [col.text.strip() for col in cols[:7]])
    print(f"Saved stats for Ryan Pressly")

if __name__ == "__main__":
    fetch_player_stats()

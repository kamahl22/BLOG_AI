import requests
from bs4 import BeautifulSoup
import csv
import os

player_id = "N/A"
player_name = "Drew Pomeranz"

def fetch_player_news():
    url = f"https://www.espn.com/mlb/player/news/_/id/{player_id}/{player_name.lower().replace(' ', '-')}"
    headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36"}
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"Error fetching news for Drew Pomeranz: {response.status_code}")
        return
    soup = BeautifulSoup(response.text, "html.parser")
    articles = soup.find_all("article")
    if not articles:
        print(f"No news found for Drew Pomeranz")
        return
    with open(os.path.join("/Users/kamahl/BLOG_AI/database/espn/mlb/teams/chicago_cubs/player/player/drew_pomeranz", "drew_pomeranz_news.csv"), "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Name", "Headline", "Date", "Summary"])
        for article in articles:
            headline = article.find("h2")
            date = article.find("time")
            summary = article.find("p")
            writer.writerow([player_name, headline.text.strip() if headline else "", date.text.strip() if date else "", summary.text.strip() if summary else ""])
    print(f"Saved news for Drew Pomeranz")

if __name__ == "__main__":
    fetch_player_news()

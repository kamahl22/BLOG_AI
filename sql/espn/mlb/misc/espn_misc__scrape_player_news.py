import requests
from bs4 import BeautifulSoup
from tabulate import tabulate

def scrape_espn_player_news():
    print("📡 Fetching ESPN MLB player news...")
    url = "https://www.espn.com/mlb/news"
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"❌ Failed to fetch ESPN page: {response.status_code}")
        return []

    soup = BeautifulSoup(response.text, "html.parser")

    news_items = soup.find_all("article") or soup.find_all("div", class_="news-item")
    if not news_items:
        print("❌ No news items found on the ESPN player news page.")
        return []

    player_news = []
    for item in news_items:
        title = item.find("h2") or item.find("h3") or item.find("a")
        title = title.text.strip() if title else "No Title"
        date = item.find("time") or item.find("span", class_="date")
        date = date.text.strip() if date else "No Date"
        summary = item.find("p") or item.find("div", class_="summary")
        summary = summary.text.strip() if summary else "No Summary"
        
        news_data = {
            "Title": title,
            "Date": date,
            "Summary": summary
        }
        player_news.append(news_data)

    print(f"✅ Scraped {len(player_news)} player news items.")
    return player_news

if __name__ == "__main__":
    news = scrape_espn_player_news()
    if news:
        headers = news[0].keys()
        rows = [item.values() for item in news]
        print("\n📊 ESPN MLB Player News:\n")
        print(tabulate(rows, headers=headers, tablefmt="grid"))
    else:
        print("❌ No news to display.")
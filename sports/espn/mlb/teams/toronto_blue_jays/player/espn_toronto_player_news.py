from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time
from tabulate import tabulate
# import supabase
# from dotenv import load_dotenv
# import os

# load_dotenv()
# client = supabase.create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

def get_blue_jays_players():
    print("📡 Fetching Toronto Blue Jays players...")
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    driver = webdriver.Chrome(options=chrome_options)
    try:
        driver.get("https://www.espn.com/mlb/team/roster/_/name/tor/toronto-blue-jays")
        time.sleep(3)
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, "html.parser")
        table = soup.find("table", class_="Table")
        if not table:
            print("❌ Roster table not found")
            return []
        players = []
        for tr in table.find("tbody").find_all("tr"):
            cells = tr.find_all("td")
            if len(cells) < 2:
                continue
            player_cell = cells[1]
            a_tag = player_cell.find("a")
            if a_tag and "href" in a_tag.attrs and "/mlb/player/" in a_tag["href"]:
                href = a_tag["href"]
                parts = href.split("/")
                if "/id/" in href:
                    try:
                        id_index = parts.index("id") + 1
                        player_id = parts[id_index]
                        player_name = parts[id_index + 1] if id_index + 1 < len(parts) else "unknown"
                        players.append({"id": player_id, "name": player_name})
                    except (IndexError, ValueError):
                        print(f"⚠️ Skipping invalid href: {href}")
        print(f"✅ Found {len(players)} Blue Jays players.")
        return players
    except Exception as e:
        print(f"❌ Error fetching players: {str(e)}")
        return []
    finally:
        driver.quit()

def scrape_blue_jays_player_news():
    print("📡 Fetching Toronto Blue Jays player news...")
    players = get_blue_jays_players()
    if not players:
        return []
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    driver = webdriver.Chrome(options=chrome_options)
    all_data = []
    for player in players[:5]:  # Limit to 5 players
        url = f"https://www.espn.com/mlb/player/news/_/id/{player['id']}/{player['name']}"
        try:
            driver.get(url)
            time.sleep(3)
            page_source = driver.page_source
            soup = BeautifulSoup(page_source, "html.parser")
            news_items = soup.find_all("article", class_="news-feed-item")
            player_news = []
            for item in news_items[:3]:  # Limit to 3 news items per player
                headline = item.find("h2")
                if headline:
                    title = headline.text.strip()
                    link = item.find("a")["href"] if item.find("a") else ""
                    player_news.append([player['name'].replace('-', ' '), title, link])
            if player_news:
                print(f"Player: {player['name'].replace('-', ' ')} News:")
                print(tabulate(player_news, headers=["Player", "Headline", "Link"], tablefmt="grid"))
                all_data.extend(player_news)
                # client.table("player_news").insert([{"team": "toronto-blue-jays", "player": row[0], "headline": row[1], "link": row[2]} for row in player_news]).execute()
        except Exception as e:
            print(f"Error scraping news for {player['name']}: {str(e)}")
    driver.quit()
    return all_data

if __name__ == "__main__":
    news = scrape_blue_jays_player_news()
    print(f"✅ Scraped {len(news)} news items." if news else "❌ No player news.")
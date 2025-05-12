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

def scrape_blue_jays_player_splits():
    print("📡 Fetching Toronto Blue Jays player splits...")
    players = get_blue_jays_players()
    if not players:
        return []
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    driver = webdriver.Chrome(options=chrome_options)
    all_data = []
    for player in players[:5]:  # Limit to 5 players
        url = f"https://www.espn.com/mlb/player/splits/_/id/{player['id']}/{player['name']}"
        try:
            print(f"Scraping splits for {player['name'].replace('-', ' ')}...")
            driver.get(url)
            time.sleep(3)
            page_source = driver.page_source
            soup = BeautifulSoup(page_source, "html.parser")
            sections = soup.find_all("h2")
            if not sections:
                print(f"⚠️ No split sections found for {player['name']}")
                continue
            for section in sections:
                section_name = section.text.strip()
                table = section.find_next("table")
                if table:
                    headers = [th.text.strip() for th in table.find("thead").find_all("th") if th.text.strip()]
                    rows = []
                    for tr in table.find("tbody").find_all("tr"):
                        row = [td.text.strip() for td in tr.find_all("td")]
                        if row:
                            rows.append(row)
                    if rows:
                        print(f"Player: {player['name'].replace('-', ' ')} - {section_name}")
                        print(tabulate(rows, headers=headers, tablefmt="grid"))
                        all_data.append({
                            "player": player['name'],
                            "section": section_name,
                            "headers": headers,
                            "rows": rows
                        })
                        # client.table("player_splits").insert([{"team": "toronto-blue-jays", "player": player['name'], "split": section_name, **dict(zip(headers, row))} for row in rows]).execute()
                    else:
                        print(f"⚠️ No data rows found for {section_name}")
                else:
                    print(f"⚠️ No table found for {section_name}")
        except Exception as e:
            print(f"Error scraping {player['name']}: {str(e)}")
    driver.quit()
    return all_data

if __name__ == "__main__":
    splits = scrape_blue_jays_player_splits()
    print(f"✅ Scraped {len(splits)} split sections." if splits else "❌ No splits data.")
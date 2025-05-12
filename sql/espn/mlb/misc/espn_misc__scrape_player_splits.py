from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time
from tabulate import tabulate

def get_mlb_players():
    print("📡 Fetching list of MLB players...")
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    driver = webdriver.Chrome(options=chrome_options)
    try:
        driver.get("https://www.espn.com/mlb/stats/player")
        time.sleep(3)  # Wait for page to load
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, "html.parser")

        # Find the player stats table
        table = soup.find("table", class_="Table")
        if not table:
            print("❌ Player stats table not found")
            return []

        rows = table.find("tbody").find_all("tr") if table.find("tbody") else []
        players = []
        for row in rows:
            cells = row.find_all("td")
            if len(cells) < 2:
                print("⚠️ Skipping row with insufficient columns")
                continue
            player_cell = cells[1]  # Player name column
            a_tag = player_cell.find("a")
            if a_tag and "href" in a_tag.attrs:
                href = a_tag["href"]
                # Expected format: /mlb/player/stats/_/id/[player-id]/[player-name]
                if "/mlb/player/" in href and "/id/" in href:
                    parts = href.split("/")
                    try:
                        id_index = parts.index("id") + 1
                        player_id = parts[id_index]
                        player_name = parts[id_index + 1] if id_index + 1 < len(parts) else "unknown"
                        players.append({"id": player_id, "name": player_name})
                    except (IndexError, ValueError):
                        print(f"⚠️ Skipping invalid href: {href}")
                        continue
                else:
                    print(f"⚠️ Skipping unexpected href format: {href}")
            else:
                print("⚠️ Skipping row with no valid player link")
        
        print(f"✅ Found {len(players)} players.")
        return players
    except Exception as e:
        print(f"❌ Error fetching player list: {str(e)}")
        return []
    finally:
        driver.quit()

def scrape_espn_mlb_player_splits():
    print("📡 Fetching ESPN MLB player splits...")
    players = get_mlb_players()
    if not players:
        print("❌ No players found to scrape splits")
        return []

    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    driver = webdriver.Chrome(options=chrome_options)
    
    all_data = []
    for player in players[:10]:  # Limit to 10 players to avoid excessive scraping
        url = f"https://www.espn.com/mlb/player/splits/_/id/{player['id']}/{player['name']}"
        try:
            print(f"Scraping splits for {player['name'].replace('-', ' ')}...")
            driver.get(url)
            time.sleep(3)  # Wait for page to load
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
                        print()
                        all_data.append({
                            "player": player['name'],
                            "section": section_name,
                            "headers": headers,
                            "rows": rows
                        })
                    else:
                        print(f"⚠️ No data rows found for {section_name}")
                else:
                    print(f"⚠️ No table found for {section_name}")
        except Exception as e:
            print(f"Error scraping {player['name']}: {str(e)}")
    
    driver.quit()
    return all_data

if __name__ == "__main__":
    splits = scrape_espn_mlb_player_splits()
    if splits:
        print(f"✅ Scraped splits for {len(splits)} split sections.")
    else:
        print("❌ No splits to display.")
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time
import supabase
from dotenv import load_dotenv
import os

load_dotenv()
client = supabase.create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

def scrape_team_stats(team_abbr, team_name):
    print(f"📡 Fetching {team_name} batting stats...")
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("user-agent=Mozilla/5.0")
    driver = webdriver.Chrome(options=chrome_options)
    try:
        url = f"https://www.espn.com/mlb/team/stats/_/name/{team_abbr}"
        driver.get(url)
        time.sleep(5)
        soup = BeautifulSoup(driver.page_source, "html.parser")
        tables = soup.find_all("table", class_="Table")
        if not tables:
            print("❌ No stats tables found")
            return []

        all_rows = []
        for table in tables:
            headers = [th.text.strip() for th in table.find("thead").find_all("th")]
            for tr in table.find("tbody").find_all("tr"):
                cells = [td.text.strip() for td in tr.find_all("td")]
                if len(cells) != len(headers):
                    continue
                row = dict(zip(headers, cells))
                row["team"] = team_name
                all_rows.append(row)

        if all_rows:
            print(f"✅ Retrieved {len(all_rows)} stat records for {team_name}")
            client.table("team_stats").delete().eq("team", team_name).execute()
            client.table("team_stats").insert(all_rows).execute()
            print("✅ Successfully inserted stats into Supabase")
        else:
            print("❌ No stat data extracted")
        return all_rows
    except Exception as e:
        print(f"Error scraping stats: {str(e)}")
        return []
    finally:
        driver.quit()

if __name__ == "__main__":
    scrape_team_stats("chc", "chicago-cubs")
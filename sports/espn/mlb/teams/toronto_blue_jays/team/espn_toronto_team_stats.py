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

def scrape_blue_jays_stats():
    print("📡 Fetching Toronto Blue Jays stats...")
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    driver = webdriver.Chrome(options=chrome_options)
    try:
        driver.get("https://www.espn.com/mlb/team/stats/_/name/tor/toronto-blue-jays")
        time.sleep(3)
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, "html.parser")
        tables = soup.find_all("table", class_="Table")
        all_data = []
        for table in tables:
            headers = [th.text.strip() for th in table.find("thead").find_all("th")]
            rows = []
            for tr in table.find("tbody").find_all("tr"):
                row = [td.text.strip() for td in tr.find_all("td")]
                if row:
                    rows.append(row)
            if rows:
                print("Toronto Blue Jays Stats:")
                print(tabulate(rows, headers=headers, tablefmt="grid"))
                all_data.extend(rows)
                # client.table("team_stats").insert([{"team": "toronto-blue-jays", **dict(zip(headers, row))} for row in rows]).execute()
        return all_data
    except Exception as e:
        print(f"Error scraping stats: {str(e)}")
        return []
    finally:
        driver.quit()

if __name__ == "__main__":
    stats = scrape_blue_jays_stats()
    print(f"✅ Scraped {len(stats)} stat entries." if stats else "❌ No stats data.")
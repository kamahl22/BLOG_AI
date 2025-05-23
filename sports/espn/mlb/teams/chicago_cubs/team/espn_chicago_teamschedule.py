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

def scrape_cubs_schedule():
    print("📡 Fetching Chicago Cubs schedule...")
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    driver = webdriver.Chrome(options=chrome_options)
    try:
        driver.get("https://www.espn.com/mlb/team/schedule/_/name/chc/chicago-cubs")
        time.sleep(3)
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, "html.parser")
        table = soup.find("table", class_="Table")
        if not table:
            print("❌ Schedule table not found")
            return []
        headers = [th.text.strip() for th in table.find("thead").find_all("th")]
        rows = []
        for tr in table.find("tbody").find_all("tr")[:10]:  # Limit to 10 games
            row = [td.text.strip() for td in tr.find_all("td")]
            if row:
                rows.append(row)
        if rows:
            print("Chicago Cubs Schedule:")
            print(tabulate(rows, headers=headers, tablefmt="grid"))
            # client.table("team_schedule").insert([{"team": "chicago-cubs", **dict(zip(headers, row))} for row in rows]).execute()
        return rows
    except Exception as e:
        print(f"Error scraping schedule: {str(e)}")
        return []
    finally:
        driver.quit()

if __name__ == "__main__":
    schedule = scrape_cubs_schedule()
    print(f"✅ Scraped {len(schedule)} schedule entries." if schedule else "❌ No schedule data.")
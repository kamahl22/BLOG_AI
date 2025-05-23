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

def scrape_cubs_injuries():
    print("📡 Fetching Chicago Cubs injuries...")
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    driver = webdriver.Chrome(options=chrome_options)
    try:
        driver.get("https://www.espn.com/mlb/team/injuries/_/name/chc/chicago-cubs")
        time.sleep(3)
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, "html.parser")
        table = soup.find("table", class_="Table")
        if not table:
            print("❌ Injuries table not found")
            return []
        headers = [th.text.strip() for th in table.find("thead").find_all("th")]
        rows = []
        for tr in table.find("tbody").find_all("tr")[:5]:  # Limit to 5 injuries
            row = [td.text.strip() for td in tr.find_all("td")]
            if row and "Out" in row[1]:  # Only active injuries
                rows.append(row)
        if rows:
            print("Chicago Cubs Injuries:")
            print(tabulate(rows, headers=headers, tablefmt="grid"))
            # client.table("team_injuries").insert([{"team": "chicago-cubs", **dict(zip(headers, row))} for row in rows]).execute()
        return rows
    except Exception as e:
        print(f"Error scraping injuries: {str(e)}")
        return []
    finally:
        driver.quit()

if __name__ == "__main__":
    injuries = scrape_cubs_injuries()
    print(f"✅ Scraped {len(injuries)} injury entries." if injuries else "❌ No injuries data.")
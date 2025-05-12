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

def scrape_blue_jays_splits():
    print("📡 Fetching Toronto Blue Jays splits...")
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    driver = webdriver.Chrome(options=chrome_options)
    try:
        driver.get("https://www.espn.com/mlb/team/splits/_/name/tor/toronto-blue-jays")
        time.sleep(3)
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, "html.parser")
        sections = soup.find_all("h2")
        all_data = []
        for section in sections:
            section_name = section.text.strip()
            table = section.find_next("table")
            if table:
                headers = [th.text.strip() for th in table.find("thead").find_all("th")]
                rows = []
                for tr in table.find("tbody").find_all("tr"):
                    row = [td.text.strip() for td in tr.find_all("td")]
                    if row:
                        rows.append(row)
                if rows:
                    print(f"Toronto Blue Jays - {section_name}:")
                    print(tabulate(rows, headers=headers, tablefmt="grid"))
                    all_data.append({"section": section_name, "headers": headers, "rows": rows})
                    # client.table("team_splits").insert([{"team": "toronto-blue-jays", "split": section_name, **dict(zip(headers, row))} for row in rows]).execute()
        return all_data
    except Exception as e:
        print(f"Error scraping splits: {str(e)}")
        return []
    finally:
        driver.quit()

if __name__ == "__main__":
    splits = scrape_blue_jays_splits()
    print(f"✅ Scraped {len(splits)} split sections." if splits else "❌ No splits data.")
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time
import re
import os
from dotenv import load_dotenv
import supabase

# Load environment variables
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Initialize Supabase client
client = supabase.create_client(SUPABASE_URL, SUPABASE_KEY)

def scrape_team_splits():
    print("📡 Fetching Chicago Cubs 2025 batting splits...")
    
    # Set up headless Chrome browser
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36")
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        # Navigate to the batting splits page
        url = "https://www.espn.com/mlb/team/splits/_/name/chc"
        driver.get(url)
        time.sleep(5)  # Wait for the page to load
        
        # Parse page content
        soup = BeautifulSoup(driver.page_source, "html.parser")
        
        # Find all tables with class 'Table'
        tables = soup.find_all("table", class_="Table")
        if not tables:
            print("❌ No tables found on the page.")
            return []
        
        # Extract batting splits data
        all_rows = []
        for table in tables:
            headers = [th.text.strip() for th in table.find("thead").find_all("th")]
            for tr in table.find("tbody").find_all("tr"):
                cells = [td.text.strip() for td in tr.find_all("td")]
                if len(cells) != len(headers):
                    continue  # Skip rows with mismatched columns
                row_data = dict(zip(headers, cells))
                row_data["team"] = "chicago-cubs"
                all_rows.append(row_data)
        
        if all_rows:
            print(f"✅ Extracted {len(all_rows)} rows of batting splits.")
            # Insert data into Supabase
            try:
                # Clear existing data for the team
                client.table("team_splits").delete().eq("team", "chicago-cubs").execute()
                # Insert new data
                client.table("team_splits").insert(all_rows).execute()
                print("✅ Successfully inserted batting splits into Supabase.")
            except Exception as e:
                print(f"❌ Supabase insertion error: {str(e)}")
        else:
            print("❌ No batting splits data extracted.")
        return all_rows
    except Exception as e:
        print(f"Error scraping batting splits: {str(e)}")
        return []
    finally:
        driver.quit()

if __name__ == "__main__":
    splits = scrape_team_splits()
    print(f"✅ Scraped {len(splits)} batting splits entries." if splits else "❌ No batting splits data.")
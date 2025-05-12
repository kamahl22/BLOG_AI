from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time
from tabulate import tabulate
import re
import supabase
from dotenv import load_dotenv
import os

load_dotenv()
client = supabase.create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

def scrape_cubs_roster():
    print("📡 Fetching Chicago Cubs roster...")
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36")
    driver = webdriver.Chrome(options=chrome_options)
    try:
        driver.get("https://www.espn.com/mlb/team/roster/_/name/chc/chicago-cubs")
        time.sleep(5)
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, "html.parser")
        tables = soup.find_all("table", class_="Table")
        if not tables:
            print("❌ No roster tables found")
            return []
        
        # Define expected columns matching ESPN website format (uppercase as in the scrape)
        espn_headers = ["Jersey", "Name", "POS", "BAT", "THW", "Age", "HT", "WT", "Birth Place"]
        
        # Define database column names (lowercase as in your SQL schema)
        db_columns = ["team", "jersey", "name", "pos", "bat", "thw", "age", "ht", "wt", "birth_place"]
        
        # Create mapping from ESPN header format to database column format
        db_column_mapping = {
            "Jersey": "jersey",
            "Name": "name",
            "POS": "pos",
            "BAT": "bat",
            "THW": "thw",
            "Age": "age",
            "HT": "ht",
            "WT": "wt",
            "Birth Place": "birth_place"
        }
        
        # Index mapping for data extraction
        index_mapping = {
            0: "jersey",    # Jersey number
            1: "name",      # Player name
            2: "pos",       # Position
            3: "bat",       # Bats
            4: "thw",       # Throws
            5: "age",       # Age
            6: "ht",        # Height
            7: "wt",        # Weight
            8: "birth_place" # Birth place
        }
        
        print(f"Using column mapping: {db_column_mapping}")
        print(f"Using index mapping: {index_mapping}")
        
        all_rows = []
        for i, table in enumerate(tables):
            print(f"Processing table {i+1}/{len(tables)}")
            raw_headers = [th.text.strip() for th in table.find("thead").find_all("th")]
            print(f"Raw headers: {raw_headers}")
            for tr in table.find("tbody").find_all("tr"):
                cells = tr.find_all("td")
                if len(cells) < 2:
                    continue
                name_cell = cells[1].text.strip()
                jersey_match = re.search(r'(\d+)$', name_cell)
                jersey = jersey_match.group(1) if jersey_match else ""
                name = re.sub(r'\d+$', '', name_cell).strip()
                row = [jersey, name] + [td.text.strip() for td in cells[2:]]
                print(f"Row: {row}")
                
                # Create a row dict using only columns that exist in the database
                row_dict = {"team": "chicago-cubs"}
                for idx, col_name in index_mapping.items():
                    if idx < len(row):
                        # Handle age column specifically to ensure it's an integer
                        if col_name == "age" and row[idx].isdigit():
                            row_dict[col_name] = int(row[idx])
                        else:
                            row_dict[col_name] = row[idx]
                
                all_rows.append(row_dict)
        
        if all_rows:
            print("Chicago Cubs Roster:")
            print(tabulate([list(r.values()) for r in all_rows], 
                          headers=list(all_rows[0].keys()), 
                          tablefmt="grid"))
            try:
                # Clear old Cubs data to ensure latest roster (handles traded players)
                client.table("team_roster").delete().eq("team", "chicago-cubs").execute()
                # Insert new data
                print(f"Inserting {len(all_rows)} rows: {all_rows[:2]}")  # Log first 2 rows
                client.table("team_roster").insert(all_rows).execute()
                print("✅ Successfully inserted roster into Supabase")
            except Exception as e:
                print(f"❌ Supabase insertion error: {str(e)}")
        else:
            print("❌ No roster data extracted")
        return all_rows
    except Exception as e:
        print(f"Error scraping roster: {str(e)}")
        return []
    finally:
        driver.quit()

if __name__ == "__main__":
    roster = scrape_cubs_roster()
    print(f"✅ Scraped {len(roster)} roster entries." if roster else "❌ No roster data.")
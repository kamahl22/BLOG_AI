# File: espn_chicago_team_splits_batting.py

import os
import time
from bs4 import BeautifulSoup
from tabulate import tabulate
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

TEAM_NAME = "Chicago Cubs"
TEAM_ID = "chc"
URL = "https://www.espn.com/mlb/team/stats/_/name/chc/chicago-cubs"

def extract_table_with_headers(table):
    rows = table.find_all("tr")
    headers = []

    thead = table.find("thead")
    if thead:
        ths = thead.find_all("th")
        headers = [th.get_text(strip=True) for th in ths]

    if not headers:
        first_row = rows[0].find_all(["td", "th"])
        headers = [cell.get_text(strip=True) for cell in first_row]
        rows = rows[1:]

    else:
        rows = rows[1:]

    data = []
    for row in rows:
        cells = row.find_all(["td", "th"])
        cell_data = [cell.get_text(strip=True) for cell in cells]
        if len(cell_data) == len(headers):
            data.append(dict(zip(headers, cell_data)))
        else:
            print(f"⚠️ Row skipped: Column mismatch:\n  Headers: {headers}\n  Cells:   {cell_data}")

    return headers, data

def fetch_batting_splits():
    print(f"📡 Fetching {TEAM_NAME} batting splits...")

    options = Options()
    options.add_argument('--headless')
    driver = webdriver.Chrome(options=options)
    driver.get(URL)
    time.sleep(5)

    soup = BeautifulSoup(driver.page_source, "html.parser")
    driver.quit()

    tables = soup.find_all("table")
    batting_table = None
    for table in tables:
        if "HR" in table.text and "OBA" in table.text:
            batting_table = table
            break

    if not batting_table:
        print("❌ No batting table found.")
        return

    headers, data = extract_table_with_headers(batting_table)

    if not data:
        print("❌ No batting split data extracted.")
        return

    print(tabulate(data, headers="keys", tablefmt="fancy_grid"))

    for row in data:
        row.update({
            "team_id": TEAM_ID,
            "team_name": TEAM_NAME,
            "category": "batting",
            "source": "espn"
        })
        supabase.table("espn_team_splits").insert(row).execute()

    print("✅ Batting splits inserted into Supabase.")

if __name__ == "__main__":
    fetch_batting_splits()
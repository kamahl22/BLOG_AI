# Team Trends Scraper
import os
import time
import pandas as pd
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# MLB teams with their URL slugs
MLB_TEAMS = [
    'arizona-diamondbacks',
    'atlanta-braves',
    'baltimore-orioles',
    'boston-red-sox',
    'chicago-cubs',
    'chicago-white-sox',
    'cincinnati-reds',
    'cleveland-guardians',
    'colorado-rockies',
    'detroit-tigers',
    'houston-astros',
    'kansas-city-royals',
    'los-angeles-angels',
    'los-angeles-dodgers',
    'miami-marlins',
    'milwaukee-brewers',
    'minnesota-twins',
    'new-york-mets',
    'new-york-yankees',
    'oakland-athletics',
    'philadelphia-phillies',
    'pittsburgh-pirates',
    'san-diego-padres',
    'san-francisco-giants',
    'seattle-mariners',
    'st-louis-cardinals',
    'tampa-bay-rays',
    'texas-rangers',
    'toronto-blue-jays',
    'washington-nationals'
]

BASE_DIR = "/Users/kamahl/BLOG_AI/sports_scripts/teamrankings/MLB/trends"

def get_timestamp():
    """Generate timestamp string for CSV header"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def fetch_and_save_table(url, team_dir, data_type):
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--user-agent=Mozilla/5.0")

    driver = webdriver.Chrome(options=options)
    print(f"Fetching: {url}")
    driver.get(url)

    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "tr-table"))
        )
        time.sleep(2)
        tables = driver.find_elements(By.CLASS_NAME, "tr-table")

        for table in tables:
            rows = table.find_elements(By.TAG_NAME, "tr")
            data = []
            for row in rows:
                cols = row.find_elements(By.TAG_NAME, "td")
                if not cols:
                    cols = row.find_elements(By.TAG_NAME, "th")
                data.append([col.text.strip() for col in cols])

            if len(data) > 1:
                df = pd.DataFrame(data[1:], columns=data[0])
                
                # Create filename with team name and data type
                team_name = team_dir.split('/')[-1].replace('-', '_')
                filename = f"{team_name}_{data_type.replace('-', '_')}.csv"
                file_path = os.path.join(team_dir, filename)
                
                # Add timestamp to the beginning of the file
                current_time = get_timestamp()
                with open(file_path, 'w') as f:
                    f.write(f"# Data scraped on: {current_time}\n")
                    df.to_csv(f, index=False)
                
                print(f"Saved to: {file_path}\n")
                print(df.head())
                break
        else:
            print("❌ No valid tables found.")

    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    
    for team in MLB_TEAMS:
        print(f"\n{'='*50}")
        print(f"SCRAPING: {team.upper().replace('-', ' ')}")
        print(f"{'='*50}")
        
        # Create team directory
        team_dir = os.path.join(BASE_DIR, team)
        os.makedirs(team_dir, exist_ok=True)
        
        # Over Under Trends
        fetch_and_save_table(
            f"https://www.teamrankings.com/mlb/team/{team}/over-under-trends",
            team_dir,
            "over-under-trends"
        )
        
        # Win Trends
        fetch_and_save_table(
            f"https://www.teamrankings.com/mlb/team/{team}/win-trends",
            team_dir,
            "win-trends"
        )
        
        # Over Under Results
        fetch_and_save_table(
            f"https://www.teamrankings.com/mlb/team/{team}/over-under-results",
            team_dir,
            "over-under-results"
        )
        
        # Run Line Results
        fetch_and_save_table(
            f"https://www.teamrankings.com/mlb/team/{team}/run-line-results",
            team_dir,
            "run-line-results"
        )
        
        # Game Log
        fetch_and_save_table(
            f"https://www.teamrankings.com/mlb/team/{team}/game-log",
            team_dir,
            "game-log"
        )
        
        # Run Line Trends
        fetch_and_save_table(
            f"https://www.teamrankings.com/mlb/team/{team}/run-line-trends",
            team_dir,
            "run-line-trends"
        )
        
        # Add small delay between teams to be respectful
        time.sleep(1)
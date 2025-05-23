# Player Stats Scraper
import os
import time
import pandas as pd
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

BASE_DIR = "/Users/kamahl/BLOG_AI/sports_scripts/teamrankings/MLB/stats/player_stats/"
os.makedirs(BASE_DIR, exist_ok=True)

def fetch_and_save_table(url, category, filename):
    output_dir = os.path.join(BASE_DIR, category)
    os.makedirs(output_dir, exist_ok=True)
    
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

                # Inside fetch_and_save_table function, replace the CSV saving block:
            if len(data) > 1:
                df = pd.DataFrame(data[1:], columns=data[0])
                file_path = os.path.join(output_dir, filename)
                
                # Add timestamp to the beginning of the file
                current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
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
    
    # Advanced Batting
    fetch_and_save_table(
        "https://www.teamrankings.com/mlb/player-stat/at-bats-per-home-run",
        "advanced_batting",
        "at-bats-per-home-run.csv"
    )
    fetch_and_save_table(
        "https://www.teamrankings.com/mlb/player-stat/batting-average-on-balls-in-play",
        "advanced_batting",
        "batting-average-on-balls-in-play.csv"
    )
    fetch_and_save_table(
        "https://www.teamrankings.com/mlb/player-stat/isolated-power",
        "advanced_batting",
        "isolated-power.csv"
    )
    fetch_and_save_table(
        "https://www.teamrankings.com/mlb/player-stat/outs-made",
        "advanced_batting",
        "outs-made.csv"
    )
    fetch_and_save_table(
        "https://www.teamrankings.com/mlb/player-stat/plate-appearances",
        "advanced_batting",
        "plate-appearances.csv"
    )
    fetch_and_save_table(
        "https://www.teamrankings.com/mlb/player-stat/secondary-average",
        "advanced_batting",
        "secondary-average.csv"
    )

    # Advanced Pitching
    fetch_and_save_table(
        "https://www.teamrankings.com/mlb/player-stat/fielding-independent-pitching",
        "advanced_pitching",
        "fielding-independent-pitching.csv"
    )
    fetch_and_save_table(
        "https://www.teamrankings.com/mlb/player-stat/hits-allowed-per-9",
        "advanced_pitching",
        "hits-allowed-per-9.csv"
    )
    fetch_and_save_table(
        "https://www.teamrankings.com/mlb/player-stat/home-runs-allowed-per-9",
        "advanced_pitching",
        "home-runs-allowed-per-9.csv"
    )
    fetch_and_save_table(
        "https://www.teamrankings.com/mlb/player-stat/pitches-per-game",
        "advanced_pitching",
        "pitches-per-game.csv"
    )
    fetch_and_save_table(
        "https://www.teamrankings.com/mlb/player-stat/pitches-per-plate-appearance",
        "advanced_pitching",
        "pitches-per-plate-appearance.csv"
    )
    fetch_and_save_table(
        "https://www.teamrankings.com/mlb/player-stat/strikeouts-per-9",
        "advanced_pitching",
        "strikeouts-per-9.csv"
    )
    fetch_and_save_table(
        "https://www.teamrankings.com/mlb/player-stat/strikeouts-per-walk",
        "advanced_pitching",
        "strikeouts-per-walk.csv"
    )
    fetch_and_save_table(
        "https://www.teamrankings.com/mlb/player-stat/walks-per-9",
        "advanced_pitching",
        "walks-per-9.csv"
    )

    # Batting
    fetch_and_save_table(
        "https://www.teamrankings.com/mlb/player-stat/at-bats",
        "batting",
        "at-bats.csv"
    )
    fetch_and_save_table(
        "https://www.teamrankings.com/mlb/player-stat/batting-average",
        "batting",
        "batting-average.csv"
    )
    fetch_and_save_table(
        "https://www.teamrankings.com/mlb/player-stat/caught-stealing",
        "batting",
        "caught-stealing.csv"
    )
    fetch_and_save_table(
        "https://www.teamrankings.com/mlb/player-stat/doubles",
        "batting",
        "doubles.csv"
    )
    fetch_and_save_table(
        "https://www.teamrankings.com/mlb/player-stat/fielding-errors",
        "batting",
        "fielding-errors.csv"
    )
    fetch_and_save_table(
        "https://www.teamrankings.com/mlb/player-stat/games-played",
        "batting",
        "games-played.csv"
    )
    fetch_and_save_table(
        "https://www.teamrankings.com/mlb/player-stat/games-started",
        "batting",
        "games-started.csv"
    )
    fetch_and_save_table(
        "https://www.teamrankings.com/mlb/player-stat/grounded-into-double-plays",
        "batting",
        "grounded-into-double-plays.csv"
    )
    fetch_and_save_table(
        "https://www.teamrankings.com/mlb/player-stat/hit-by-pitch",
        "batting",
        "hit-by-pitch.csv"
    )
    fetch_and_save_table(
        "https://www.teamrankings.com/mlb/player-stat/hits",
        "batting",
        "hits.csv"
    )
    fetch_and_save_table(
        "https://www.teamrankings.com/mlb/player-stat/home-runs",
        "batting",
        "home-runs.csv"
    )
    fetch_and_save_table(
        "https://www.teamrankings.com/mlb/player-stat/intentional-walks",
        "batting",
        "intentional-walks.csv"
    )
    fetch_and_save_table(
        "https://www.teamrankings.com/mlb/player-stat/left-on-base",
        "batting",
        "left-on-base.csv"
    )
    fetch_and_save_table(
        "https://www.teamrankings.com/mlb/player-stat/on-base-pct",
        "batting",
        "on-base-pct.csv"
    )
    fetch_and_save_table(
        "https://www.teamrankings.com/mlb/player-stat/on-base-plus-slugging",
        "batting",
        "on-base-plus-slugging.csv"
    )
    fetch_and_save_table(
        "https://www.teamrankings.com/mlb/player-stat/runners-left-in-scoring-position",
        "batting",
        "runners-left-in-scoring-position.csv"
    )
    fetch_and_save_table(
        "https://www.teamrankings.com/mlb/player-stat/runs",
        "batting",
        "runs.csv"
    )
    fetch_and_save_table(
        "https://www.teamrankings.com/mlb/player-stat/runs-batted-in",
        "batting",
        "runs-batted-in.csv"
    )
    fetch_and_save_table(
        "https://www.teamrankings.com/mlb/player-stat/singles",
        "batting",
        "singles.csv"
    )
    fetch_and_save_table(
        "https://www.teamrankings.com/mlb/player-stat/slugging-pct",
        "batting",
        "slugging-pct.csv"
    )
    fetch_and_save_table(
        "https://www.teamrankings.com/mlb/player-stat/stolen-bases",
        "batting",
        "stolen-bases.csv"
    )
    fetch_and_save_table(
        "https://www.teamrankings.com/mlb/player-stat/strikeouts",
        "batting",
        "strikeouts.csv"
    )
    fetch_and_save_table(
        "https://www.teamrankings.com/mlb/player-stat/total-bases",
        "batting",
        "total-bases.csv"
    )
    fetch_and_save_table(
        "https://www.teamrankings.com/mlb/player-stat/triples",
        "batting",
        "triples.csv"
    )
    fetch_and_save_table(
        "https://www.teamrankings.com/mlb/player-stat/two-out-rbis",
        "batting",
        "two-out-rbis.csv"
    )
    fetch_and_save_table(
        "https://www.teamrankings.com/mlb/player-stat/walks",
        "batting",
        "walks.csv"
    )

    # Batting Events
    fetch_and_save_table(
        "https://www.teamrankings.com/mlb/player-stat/games-with-two-plus-total-bases",
        "batting_events",
        "games-with-two-plus-total-bases.csv"
    )
    fetch_and_save_table(
        "https://www.teamrankings.com/mlb/player-stat/games-with-a-hit",
        "batting_events",
        "games-with-a-hit.csv"
    )
    fetch_and_save_table(
        "https://www.teamrankings.com/mlb/player-stat/games-with-a-home-run",
        "batting_events",
        "games-with-a-home-run.csv"
    )
    fetch_and_save_table(
        "https://www.teamrankings.com/mlb/player-stat/games-with-a-run",
        "batting_events",
        "games-with-a-run.csv"
    )
    fetch_and_save_table(
        "https://www.teamrankings.com/mlb/player-stat/games-with-a-run-batted-in",
        "batting_events",
        "games-with-a-run-batted-in.csv"
    )
    fetch_and_save_table(
        "https://www.teamrankings.com/mlb/player-stat/games-with-a-stolen-base",
        "batting_events",
        "games-with-a-stolen-base.csv"
    )
    fetch_and_save_table(
        "https://www.teamrankings.com/mlb/player-stat/percent-of-games-with-two-plus-total-bases",
        "batting_events",
        "percent-of-games-with-two-plus-total-bases.csv"
    )
    fetch_and_save_table(
        "https://www.teamrankings.com/mlb/player-stat/percent-of-games-with-a-hit",
        "batting_events",
        "percent-of-games-with-a-hit.csv"
    )
    fetch_and_save_table(
        "https://www.teamrankings.com/mlb/player-stat/percent-of-games-with-a-home-run",
        "batting_events",
        "percent-of-games-with-a-home-run.csv"
    )
    fetch_and_save_table(
        "https://www.teamrankings.com/mlb/player-stat/percent-of-games-with-a-run",
        "batting_events",
        "percent-of-games-with-a-run.csv"
    )
    fetch_and_save_table(
        "https://www.teamrankings.com/mlb/player-stat/percent-of-games-with-a-run-batted-in",
        "batting_events",
        "percent-of-games-with-a-run-batted-in.csv"
    )
    fetch_and_save_table(
        "https://www.teamrankings.com/mlb/player-stat/percent-of-games-with-a-stolen-base",
        "batting_events",
        "percent-of-games-with-a-stolen-base.csv"
    )
    fetch_and_save_table(
        "https://www.teamrankings.com/mlb/player-stat/percent-of-starts-with-two-plus-total-bases",
        "batting_events",
        "percent-of-starts-with-two-plus-total-bases.csv"
    )
    fetch_and_save_table(
        "https://www.teamrankings.com/mlb/player-stat/percent-of-starts-with-a-hit",
        "batting_events",
        "percent-of-starts-with-a-hit.csv"
    )
    fetch_and_save_table(
        "https://www.teamrankings.com/mlb/player-stat/percent-of-starts-with-a-home-run",
        "batting_events",
        "percent-of-starts-with-a-home-run.csv"
    )
    fetch_and_save_table(
        "https://www.teamrankings.com/mlb/player-stat/percent-of-starts-with-a-run",
        "batting_events",
        "percent-of-starts-with-a-run.csv"
    )
    fetch_and_save_table(
        "https://www.teamrankings.com/mlb/player-stat/percent-of-starts-with-a-run-batted-in",
        "batting_events",
        "percent-of-starts-with-a-run-batted-in.csv"
    )
    fetch_and_save_table(
        "https://www.teamrankings.com/mlb/player-stat/percent-of-starts-with-a-stolen-base",
        "batting_events",
        "percent-of-starts-with-a-stolen-base.csv"
    )

    # Batting Ratios
    fetch_and_save_table(
        "https://www.teamrankings.com/mlb/player-stat/base-on-balls-pct",
        "batting_ratios",
        "base-on-balls-pct.csv"
    )
    fetch_and_save_table(
        "https://www.teamrankings.com/mlb/player-stat/extra-base-hit-pct",
        "batting_ratios",
        "extra-base-hit-pct.csv"
    )
    fetch_and_save_table(
        "https://www.teamrankings.com/mlb/player-stat/hits-for-extra-bases-pct",
        "batting_ratios",
        "hits-for-extra-bases-pct.csv"
    )
    fetch_and_save_table(
        "https://www.teamrankings.com/mlb/player-stat/home-run-pct",
        "batting_ratios",
        "home-run-pct.csv"
    )
    fetch_and_save_table(
        "https://www.teamrankings.com/mlb/player-stat/stolen-base-pct",
        "batting_ratios",
        "stolen-base-pct.csv"
    )
    fetch_and_save_table(
        "https://www.teamrankings.com/mlb/player-stat/strikeout-pct",
        "batting_ratios",
        "strikeout-pct.csv"
    )

    # Pitching
    fetch_and_save_table(
        "https://www.teamrankings.com/mlb/player-stat/batters-faced",
        "pitching",
        "batters-faced.csv"
    )
    fetch_and_save_table(
        "https://www.teamrankings.com/mlb/player-stat/earned-run-average",
        "pitching",
        "earned-run-average.csv"
    )
    fetch_and_save_table(
        "https://www.teamrankings.com/mlb/player-stat/earned-runs-allowed",
        "pitching",
        "earned-runs-allowed.csv"
    )
    fetch_and_save_table(
        "https://www.teamrankings.com/mlb/player-stat/fly-ball-outs",
        "pitching",
        "fly-ball-outs.csv"
    )
    fetch_and_save_table(
        "https://www.teamrankings.com/mlb/player-stat/games-pitched",
        "pitching",
        "games-pitched.csv"
    )
    fetch_and_save_table(
        "https://www.teamrankings.com/mlb/player-stat/games-started",
        "pitching",
        "games-started.csv"
    )
    fetch_and_save_table(
        "https://www.teamrankings.com/mlb/player-stat/ground-ball-outs",
        "pitching",
        "ground-ball-outs.csv"
    )
    fetch_and_save_table(
        "https://www.teamrankings.com/mlb/player-stat/hits-allowed",
        "pitching",
        "hits-allowed.csv"
    )
    fetch_and_save_table(
        "https://www.teamrankings.com/mlb/player-stat/home-runs-allowed",
        "pitching",
        "home-runs-allowed.csv"
    )
    fetch_and_save_table(
        "https://www.teamrankings.com/mlb/player-stat/innings-pitched",
        "pitching",
        "innings-pitched.csv"
    )
    fetch_and_save_table(
        "https://www.teamrankings.com/mlb/player-stat/pitches-thrown",
        "pitching",
        "pitches-thrown.csv"
    )
    fetch_and_save_table(
        "https://www.teamrankings.com/mlb/player-stat/runs-allowed",
        "pitching",
        "runs-allowed.csv"
    )
    fetch_and_save_table(
        "https://www.teamrankings.com/mlb/player-stat/strikeouts",
        "pitching",
        "strikeouts.csv"
    )
    fetch_and_save_table(
        "https://www.teamrankings.com/mlb/player-stat/strikes-thrown",
        "pitching",
        "strikes-thrown.csv"
    )
    fetch_and_save_table(
        "https://www.teamrankings.com/mlb/player-stat/walks",
        "pitching",
        "walks.csv"
    )
    fetch_and_save_table(
        "https://www.teamrankings.com/mlb/player-stat/walks-plus-hits-per-inning-pitched",
        "pitching",
        "walks-plus-hits-per-inning-pitched.csv"
    )

    # Pitching Ratios
    fetch_and_save_table(
        "https://www.teamrankings.com/mlb/player-stat/ground-outs-to-air-outs",
        "pitching_ratios",
        "ground-outs-to-air-outs.csv"
    )
    fetch_and_save_table(
        "https://www.teamrankings.com/mlb/player-stat/home-run-pct",
        "pitching_ratios",
        "home-run-pct.csv"
    )
    fetch_and_save_table(
        "https://www.teamrankings.com/mlb/player-stat/strike-pct",
        "pitching_ratios",
        "strike-pct.csv"
    )
    fetch_and_save_table(
        "https://www.teamrankings.com/mlb/player-stat/strikeout-pct",
        "pitching_ratios",
        "strikeout-pct.csv"
    )
    fetch_and_save_table(
        "https://www.teamrankings.com/mlb/player-stat/walk-pct",
        "pitching_ratios",
        "walk-pct.csv"
    )

    # Pitching Results
    fetch_and_save_table(
        "https://www.teamrankings.com/mlb/player-stat/blown-saves",
        "pitching_results",
        "blown-saves.csv"
    )
    fetch_and_save_table(
        "https://www.teamrankings.com/mlb/player-stat/cheap-wins",
        "pitching_results",
        "cheap-wins.csv"
    )
    fetch_and_save_table(
        "https://www.teamrankings.com/mlb/player-stat/complete-games",
        "pitching_results",
        "complete-games.csv"
    )
    fetch_and_save_table(
        "https://www.teamrankings.com/mlb/player-stat/holds",
        "pitching_results",
        "holds.csv"
    )
    fetch_and_save_table(
        "https://www.teamrankings.com/mlb/player-stat/losses",
        "pitching_results",
        "losses.csv"
    )
    fetch_and_save_table(
        "https://www.teamrankings.com/mlb/player-stat/no-decisions",
        "pitching_results",
        "no-decisions.csv"
    )
    fetch_and_save_table(
        "https://www.teamrankings.com/mlb/player-stat/percent-of-starts-won",
        "pitching_results",
        "percent-of-starts-won.csv"
    )
    fetch_and_save_table(
        "https://www.teamrankings.com/mlb/player-stat/quality-start-pct",
        "pitching_results",
        "quality-start-pct.csv"
    )
    fetch_and_save_table(
        "https://www.teamrankings.com/mlb/player-stat/quality-starts",
        "pitching_results",
        "quality-starts.csv"
    )
    fetch_and_save_table(
        "https://www.teamrankings.com/mlb/player-stat/save-pct",
        "pitching_results",
        "save-pct.csv"
    )
    fetch_and_save_table(
        "https://www.teamrankings.com/mlb/player-stat/saves",
        "pitching_results",
        "saves.csv"
    )
    fetch_and_save_table(
        "https://www.teamrankings.com/mlb/player-stat/shutouts",
        "pitching_results",
        "shutouts.csv"
    )
    fetch_and_save_table(
        "https://www.teamrankings.com/mlb/player-stat/tough-losses",
        "pitching_results",
        "tough-losses.csv"
    )
    fetch_and_save_table(
        "https://www.teamrankings.com/mlb/player-stat/win-pct",
        "pitching_results",
        "win-pct.csv"
    )
    fetch_and_save_table(
        "https://www.teamrankings.com/mlb/player-stat/wins",
        "pitching_results",
        "wins.csv"
    )
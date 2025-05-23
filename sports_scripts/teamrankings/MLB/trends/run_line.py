import time
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import os

# Base directory for saving files
BASE_DIR = "/Users/kamahl/BLOG_AI/sports_scripts/teamrankings/MLB/trends/chicago-cubs"
os.makedirs(BASE_DIR, exist_ok=True)

def fetch_and_save_chicago_cubs_run_line_trends():
    """Fetch and save Chicago Cubs Run Line trends from TeamRankings."""
    url = "https://www.teamrankings.com/mlb/team/chicago-cubs/run-line-trends"

    # Set up headless Firefox
    options = Options()
    options.headless = True
    driver = webdriver.Firefox(options=options)

    print("Fetching Run Line trends for Chicago Cubs")
    driver.get(url)

    # Wait for the table to load (up to 10 seconds)
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "tr-table"))
        )
        time.sleep(2)
    except Exception as e:
        print(f"Error waiting for table: {e}")
        driver.quit()
        return None

    tables = driver.find_elements(By.TAG_NAME, "table")
    print(f"Number of tables found: {len(tables)}")

    if not tables:
        print("No tables found.")
        driver.quit()
        return None

    data = []
    for table in tables:
        if "tr-table" in table.get_attribute("class"):
            rows = table.find_elements(By.TAG_NAME, "tr")
            print(f"Number of rows in table: {len(rows)}")

            for row in rows[1:]:  # Skip header
                cols = row.find_elements(By.TAG_NAME, "td")
                if len(cols) >= 5:
                    row_data = [col.text.strip() for col in cols[:5]]
                    print(f"Row data: {row_data}")
                    data.append(row_data)

    driver.quit()

    if not data:
        print("No data extracted.")
        return None

    # Create DataFrame
    df = pd.DataFrame(data, columns=["Trend", "Run Line Record", "Cover %", "MOV", "Run Line +/-"])

    # Save to CSV
    csv_filename = os.path.join(BASE_DIR, "chicago-cubs", "chicago-cubs_run_line_trends.csv")
    os.makedirs(os.path.dirname(csv_filename), exist_ok=True)
    df.to_csv(csv_filename, index=False)
    print(f"CSV file saved: {csv_filename}")

    # Print formatted table
    print(f"\nRun Line Trends for Chicago Cubs")
    col_widths = [max(len(str(row[i])) for row in data + [df.columns]) for i in range(5)]
    top_border = "┌" + "─".join("─" * (w + 2) for w in col_widths) + "┐"
    bottom_border = "└" + "─".join("─" * (w + 2) for w in col_widths) + "┘"
    separator = "├" + "─".join("─" * (w + 2) for w in col_widths) + "┤"

    header_row = "│ " + " │ ".join(h.center(w) for h, w in zip(df.columns, col_widths)) + " │"
    print(top_border)
    print(header_row)
    print(separator)

    for row in data:
        row_str = "│ " + " │ ".join(str(item).ljust(w) for item, w in zip(row, col_widths)) + " │"
        print(row_str)
    print(bottom_border)

    return df

if __name__ == "__main__":
    fetch_and_save_chicago_cubs_run_line_trends()
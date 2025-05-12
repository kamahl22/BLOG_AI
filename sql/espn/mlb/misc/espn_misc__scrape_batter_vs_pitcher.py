import requests
from bs4 import BeautifulSoup
from tabulate import tabulate

def scrape_espn_batter_vs_pitcher():
    print("📡 Fetching ESPN MLB batter vs. pitcher stats...")
    url = "https://www.espn.com/mlb/stats/battervspitcher"
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"❌ Failed to fetch ESPN page: {response.status_code}")
        return []

    soup = BeautifulSoup(response.text, "html.parser")

    tables = soup.find_all("table")
    if not tables:
        print("❌ No tables found on the ESPN batter vs. pitcher page.")
        return []

    max_columns = 0
    bvp_table = None
    for table in tables:
        headers = table.find("thead")
        if headers:
            columns = headers.find_all("th")
            if len(columns) > max_columns:
                max_columns = len(columns)
                bvp_table = table

    if not bvp_table:
        print("❌ Could not find the batter vs. pitcher table.")
        return []

    headers = [th.text.strip() for th in bvp_table.find("thead").find_all("th")]
    rows = bvp_table.find("tbody").find_all("tr")

    bvp_stats = []
    for row in rows:
        cols = [td.text.strip() for td in row.find_all("td")]
        if cols and len(cols) == len(headers):
            bvp_data = dict(zip(headers, cols))
            bvp_stats.append(bvp_data)

    print(f"✅ Scraped {len(bvp_stats)} batter vs. pitcher records.")
    return bvp_stats

if __name__ == "__main__":
    stats = scrape_espn_batter_vs_pitcher()
    if stats:
        headers = stats[0].keys()
        rows = [stat.values() for stat in stats]
        print("\n📊 ESPN MLB Batter vs. Pitcher Stats:\n")
        print(tabulate(rows, headers=headers, tablefmt="grid"))
    else:
        print("❌ No stats to display.")
import requests
from bs4 import BeautifulSoup
from tabulate import tabulate

def scrape_espn_mlb_team_injuries():
    print("📡 Fetching ESPN MLB team injuries...")
    url = "https://www.espn.com/mlb/injuries"
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
        print("❌ No tables found on the ESPN injuries page.")
        return []

    injuries = []
    for table in tables:
        team_name = table.find_previous("h2") or table.find_previous("h3")
        team_name = team_name.text.strip() if team_name else "Unknown Team"
        headers = [th.text.strip() for th in table.find("thead").find_all("th")] if table.find("thead") else ["Player", "Status", "Details"]
        rows = table.find("tbody").find_all("tr") if table.find("tbody") else []
        
        for row in rows:
            cols = [td.text.strip() for td in row.find_all("td")]
            if cols and len(cols) >= 2:
                injury_data = {"Team": team_name}
                injury_data.update(dict(zip(headers, cols)))
                injuries.append(injury_data)

    print(f"✅ Scraped {len(injuries)} injury records.")
    return injuries

if __name__ == "__main__":
    injuries = scrape_espn_mlb_team_injuries()
    if injuries:
        headers = injuries[0].keys()
        rows = [injury.values() for injury in injuries]
        print("\n📊 ESPN MLB Team Injuries:\n")
        print(tabulate(rows, headers=headers, tablefmt="grid"))
    else:
        print("❌ No injuries to display.")
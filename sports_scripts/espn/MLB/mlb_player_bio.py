import os
import requests
import csv
from tabulate import tabulate

def fetch_player_bio(player_id: int):
    url = f"https://site.api.espn.com/apis/site/v2/sports/baseball/mlb/athletes/{player_id}"
    response = requests.get(url)
    if response.status_code != 200:
        print("Failed to fetch data.")
        return None

    data = response.json()
    bio = {
        "Name": data.get("fullName"),
        "Team": data.get("team", {}).get("displayName"),
        "Position": data.get("position", {}).get("name"),
        "Age": data.get("age"),
        "Height": data.get("height"),
        "Weight": data.get("weight"),
        "Birthplace": data.get("birthPlace", {}).get("city", ""),
        "College": data.get("college", {}).get("name", "N/A"),
        "Experience": data.get("experience", {}).get("years", "N/A"),
        "Jersey": data.get("jersey")
    }
    return bio

def save_bio_to_csv(bio, file_path):
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["Field", "Value"])
        for key, value in bio.items():
            writer.writerow([key, value])

def display_bio_table(bio):
    table = [(key, value) for key, value in bio.items()]
    print(tabulate(table, headers=["Field", "Value"], tablefmt="fancy_grid"))

if __name__ == "__main__":
    player_id = 40938  # Seiya Suzuki's ESPN player ID
    team_name = "cubs"
    player_name = "seiya_suzuki"
    
    bio = fetch_player_bio(player_id)
    if bio:
        display_bio_table(bio)
        csv_path = f"mlb_test/{team_name}/{player_name}/{player_name}_bio.csv"
        save_bio_to_csv(bio, csv_path)
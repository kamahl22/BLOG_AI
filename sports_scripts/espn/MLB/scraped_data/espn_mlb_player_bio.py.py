import requests
import csv
import os
from bs4 import BeautifulSoup

player_id = "4142424"
player_name = "Seiya Suzuki"

def fetch_and_save_bio():
    url = f"https://www.espn.com/mlb/player/bio/_/id/{player_id}/{player_name.lower().replace(' ', '-')}"
    
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    response = requests.get(url, headers=headers)
    
    print(f"Status Code: {response.status_code}")
    if response.status_code != 200:
        print(f"Error fetching bio for {player_name}")
        return None, None
    
    soup = BeautifulSoup(response.text, "html.parser")

    # Look for bio rows in the content
    bio_data = {}
    bio_list = soup.find_all("li", class_="AnchorLink")

    if not bio_list:
        # Fallback: look for a more general container with spans inside list items
        bio_list = soup.select("ul li span")

    # More consistent bio container (2025 verified)
    container = soup.find_all("li", class_="InlineFlex")

    for item in container:
        spans = item.find_all("span")
        if len(spans) == 2:
            key = spans[0].get_text(strip=True).rstrip(":")
            value = spans[1].get_text(strip=True)
            bio_data[key] = value

    # Career History fallback — custom logic if it exists
    if "Career History" not in bio_data:
        career_header = soup.find("h2", string="Career History")
        if career_header:
            history_list = career_header.find_next("ul")
            if history_list:
                items = history_list.find_all("li")
                bio_data["Career History"] = "; ".join(li.get_text(strip=True) for li in items)

    if not bio_data:
        print(f"No bio data found for {player_name}.")
        return None, None

    expected_fields = ["Team", "Position", "HT/WT", "Birthdate", "Birthplace", "Status", "Experience", "Career History"]
    player_bio_dict = {field: bio_data.get(field, "N/A") for field in expected_fields}
    bio_data_rows = [[field, player_bio_dict[field]] for field in expected_fields]

    base_directory = "/Users/kamahl/BLOG_AI/database/espn/mlb/teams/chicago_cubs/player/player/seiya_suzuki"
    player_folder = os.path.join(base_directory, "chicago-cubs", "seiya_suzuki")
    os.makedirs(player_folder, exist_ok=True)
    
    csv_filename = os.path.join(player_folder, f"{player_name.lower().replace(' ', '_')}_bio.csv")
    with open(csv_filename, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["Field", "Value"])
        writer.writerows(bio_data_rows)

    print(f"CSV file saved: {csv_filename}")
    return ["Field", "Value"], bio_data_rows


def print_excel_style():
    headers, data = fetch_and_save_bio()
    if not headers or not data:
        print("No headers or data to display.")
        return
    
    max_cols = len(headers)
    col_widths = [len(str(h)) for h in headers]
    
    for row in data:
        padded_row = row + [""] * (max_cols - len(row)) if len(row) < max_cols else row[:max_cols]
        for i, cell in enumerate(padded_row):
            col_widths[i] = max(col_widths[i], len(str(cell)))
    
    top_border = "┌" + "─".join("─" * (w + 2) for w in col_widths) + "┐"
    bottom_border = "└" + "─".join("─" * (w + 2) for w in col_widths) + "┘"
    separator = "├" + "─".join("─" * (w + 2) for w in col_widths) + "┤"
    
    print(top_border)
    header_row = "│ " + " │ ".join(h.center(w) for h, w in zip(headers, col_widths)) + " │"
    print(header_row)
    print(separator)
    
    for row in data:
        padded_row = row + [""] * (max_cols - len(row)) if len(row) < max_cols else row[:max_cols]
        data_row = "│ " + " │ ".join(str(cell).ljust(w) for cell, w in zip(padded_row, col_widths)) + " │"
        print(data_row)
    
    print(bottom_border)


if __name__ == "__main__":
    print_excel_style()
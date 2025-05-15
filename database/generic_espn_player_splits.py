import requests
import csv
import os
from bs4 import BeautifulSoup
import sys

def fetch_player_splits(player_id, player_name):
    """Fetch player splits data from ESPN"""
    url = f"https://www.espn.com/mlb/player/splits/_/id/{player_id}/{player_name.lower().replace(' ', '-')}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    }
    
    print(f"Fetching data for {player_name} (ID: {player_id}) from {url}")
    response = requests.get(url, headers=headers)

    print(f"Status Code: {response.status_code}")
    if response.status_code != 200:
        print(f"Error: Unable to fetch data for {player_name} (ID: {player_id}) - Status Code {response.status_code}")
        return None

    return response.text

def parse_splits_data(html_content):
    """Parse the HTML content to extract player splits data"""
    soup = BeautifulSoup(html_content, "html.parser")
    tables = soup.find_all("table", class_="Table")
    
    if not tables:
        print("No stats tables found. The page structure may have changed.")
        return None, None

    # Headers we expect to find in the splits data
    expected_stats_headers = ["AB", "R", "H", "2B", "3B", "HR", "RBI", "BB", "HBP", "SO", "SB", "CS", "AVG", "OBP", "SLG", "OPS"]
    
    # Categories and their splits
    categories = {
        "OVERALL": ["OVERALL"],
        "BREAKDOWN": ["vs. Left", "vs. Right", "Home", "Away", "Day", "Night"],
        "DAY/MONTH": ["March", "April", "May", "June", "July", "August", "September", "Last 7 Days", "Last 15 Days", "Last 30 Days"],
        "OPPONENT": ["vs. ARI", "vs. ATL", "vs. BAL", "vs. BOS", "vs. CHC", "vs. CIN", "vs. CLE", "vs. COL", "vs. CWS", "vs. DET", 
                    "vs. HOU", "vs. KC", "vs. LAA", "vs. LAD", "vs. MIA", "vs. MIL", "vs. MIN", "vs. NYM", "vs. NYY", "vs. OAK", 
                    "vs. PHI", "vs. PIT", "vs. SD", "vs. SEA", "vs. SF", "vs. STL", "vs. TB", "vs. TEX", "vs. TOR", "vs. WSH"],
        "STADIUM": ["American Family Field", "Angel Stadium", "Busch Stadium", "Chase Field", "Citi Field", "Citizens Bank Park", 
                   "Comerica Park", "Coors Field", "Dodger Stadium", "Fenway Park", "Globe Life Field", "Great American Ball Park", 
                   "Guaranteed Rate Field", "Kauffman Stadium", "LoanDepot Park", "Minute Maid Park", "Nationals Park", "Oracle Park", 
                   "PETCO Park", "PNC Park", "Progressive Field", "Rogers Centre", "T-Mobile Park", "Target Field", "Tropicana Field", 
                   "Truist Park", "Wrigley Field", "Yankee Stadium"],
        "POSITION": ["As C", "As 1B", "As 2B", "As 3B", "As SS", "As LF", "As CF", "As RF", "As DH"], 
        "COUNT": ["Count 0-0", "Count 0-1", "Count 0-2", "Count 1-0", "Count 1-1", "Count 1-2", "Count 2-0", "Count 2-1", "Count 2-2", 
                 "Count 3-0", "Count 3-1", "Count 3-2"],
        "BATTING ORDER": ["Batting #1", "Batting #2", "Batting #3", "Batting #4", "Batting #5", "Batting #6", "Batting #7", "Batting #8", "Batting #9"],
        "SITUATION": ["None On", "Runners On", "Scoring Position", "Bases Loaded", "Lead Off Inning", "Scoring Position, 2 Out"]
    }
    
    all_categories_with_headers = []
    for category, splits in categories.items():
        all_categories_with_headers.append(category)
        all_categories_with_headers.extend(splits)
    
    # Dictionary to store all the stats
    player_stats = {}
    
    # Process each table row
    for table in tables:
        rows = table.find_all("tr")
        current_category = None
        
        for row in rows:
            cells = row.find_all("td")
            if not cells:
                continue
                
            cell_texts = [cell.get_text(strip=True) for cell in cells]
            
            # Skip empty rows
            if not cell_texts or all(not text for text in cell_texts):
                continue
            
            # Check if this is a category header row
            if len(cell_texts) == 1 and cell_texts[0] in categories.keys():
                current_category = cell_texts[0]
                continue
                
            # Check if this is a split row (could be in the first or second column)
            split_name = None
            stats_start_idx = 0
            
            # First, check if the first cell is a valid split
            if cell_texts[0] in all_categories_with_headers:
                split_name = cell_texts[0]
                stats_start_idx = 1
            # Then check if the second cell might be a valid split (when the first cell is empty)
            elif len(cell_texts) > 1 and cell_texts[1] in all_categories_with_headers:
                split_name = cell_texts[1]
                stats_start_idx = 2
            
            # If not in our predefined list, try to match by pattern
            if not split_name and len(cell_texts) > 1:
                # Check for opponent pattern (vs. XXX)
                if cell_texts[0].startswith("vs.") or (len(cell_texts) > 1 and cell_texts[1].startswith("vs.")):
                    idx = 0 if cell_texts[0].startswith("vs.") else 1
                    split_name = cell_texts[idx]
                    stats_start_idx = idx + 1
                    if "OPPONENT" not in player_stats:
                        player_stats["OPPONENT"] = {}
                    current_category = "OPPONENT"
                
                # Check for stadium pattern
                elif any(stadium_keyword in cell_texts[0].lower() or 
                       (len(cell_texts) > 1 and stadium_keyword in cell_texts[1].lower()) 
                       for stadium_keyword in ["park", "field", "stadium", "centre"]):
                    idx = 0
                    # Find which cell contains the stadium name
                    for i, text in enumerate(cell_texts[:2]):
                        if any(keyword in text.lower() for keyword in ["park", "field", "stadium", "centre"]):
                            idx = i
                            break
                    split_name = cell_texts[idx]
                    stats_start_idx = idx + 1
                    if "STADIUM" not in player_stats:
                        player_stats["STADIUM"] = {}
                    current_category = "STADIUM"
            
            # Process stats row if we found a valid split
            if split_name and len(cell_texts) > stats_start_idx:
                stats = cell_texts[stats_start_idx:]
                
                # Convert split name to category and actual split
                category_for_split = None
                for cat, splits in categories.items():
                    if split_name in splits:
                        category_for_split = cat
                        break
                
                # If not found in predefined categories, use the current category context
                if not category_for_split and current_category:
                    category_for_split = current_category
                
                # Handle category header rows (they should be category name, not a split)
                if split_name in categories.keys():
                    category_for_split = split_name
                    split_name = split_name  # Keep it the same for headers
                
                # Store the data with proper structure
                if category_for_split not in player_stats:
                    player_stats[category_for_split] = {}
                
                if split_name not in player_stats[category_for_split]:
                    player_stats[category_for_split][split_name] = stats
    
    return player_stats, expected_stats_headers

def format_and_save_csv(player_name, player_stats, stats_headers, base_directory):
    """Format and save the player stats data to a CSV file"""
    # Create directory if it doesn't exist
    player_directory = os.path.join(base_directory, player_name.lower().replace(' ', '_'))
    os.makedirs(player_directory, exist_ok=True)
    
    csv_filename = os.path.join(player_directory, f"{player_name.lower().replace(' ', '_')}_splits.csv")
    
    # Prepare CSV data with headers
    csv_data = []
    
    # Add header row with "Split Type", "Split Value", and all stat columns
    csv_headers = ["Split Type", "Split Value"] + stats_headers
    csv_data.append(csv_headers)
    
    # Categories order to match the screenshot
    category_order = ["OVERALL", "BREAKDOWN", "DAY/MONTH", "OPPONENT", "STADIUM", "POSITION", "COUNT", "BATTING ORDER", "SITUATION"]
    
    # Add data rows organized by categories
    for category in category_order:
        if category in player_stats:
            # Add category row first
            category_row = [category, ""] + [""] * len(stats_headers)
            csv_data.append(category_row)
            
            # Add each split within the category
            for split, stats in player_stats[category].items():
                # Skip if this is just the category name again
                if split == category:
                    continue
                
                # Ensure we have the right number of stats (pad with empty strings if needed)
                padded_stats = stats + [""] * (len(stats_headers) - len(stats))
                split_row = ["", split] + padded_stats[:len(stats_headers)]
                csv_data.append(split_row)
    
    # Write to CSV
    with open(csv_filename, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerows(csv_data)
    
    print(f"✅ CSV file saved: {csv_filename}")
    return csv_data

def print_table(data, player_name, year="2025"):
    """Pretty print the table in a format similar to the screenshot."""
    print(f"\n{year} Splits for {player_name}")
    
    # Calculate column widths
    col_widths = [max(len(str(row[i])) for row in data) for i in range(len(data[0]))]
    
    # Header separators
    top_border = "┌" + "┬".join("─" * (w + 2) for w in col_widths) + "┐"
    header_separator = "├" + "┼".join("─" * (w + 2) for w in col_widths) + "┤"
    category_separator = "├" + "┼".join("─" * (w + 2) for w in col_widths) + "┤"
    bottom_border = "└" + "┴".join("─" * (w + 2) for w in col_widths) + "┘"
    
    # Print top border
    print(top_border)
    
    # Print headers
    header_row = "│ " + " │ ".join(str(data[0][i]).center(col_widths[i]) for i in range(len(data[0]))) + " │"
    print(header_row)
    print(header_separator)
    
    # Print data with category separators
    last_category = None
    for row_idx, row in enumerate(data[1:], 1):
        # Check if this is a category header row
        is_category = row[0] and not row[1]
        
        if is_category:
            if last_category:  # Don't print separator before the first category
                print(category_separator)
            last_category = row[0]
        
        # Format and print the row
        formatted_row = "│ " + " │ ".join(str(row[i]).ljust(col_widths[i]) for i in range(len(row))) + " │"
        print(formatted_row)
    
    # Print bottom border
    print(bottom_border)

def main():
    """Main function to run the script"""
    # Check if command line arguments are provided
    if len(sys.argv) >= 3:
        player_id = sys.argv[1]
        player_name = sys.argv[2]
    else:
        # Default values if no arguments are provided
        player_id = "40718"
        player_name = "Seiya Suzuki"
    
    # Set the base directory
    base_directory = "/Users/kamahl/BLOG_AI/database/espn/mlb/teams/chicago_cubs/player"
    
    # Fetch the HTML content
    html_content = fetch_player_splits(player_id, player_name)
    if not html_content:
        return
    
    # Parse the data
    player_stats, stats_headers = parse_splits_data(html_content)
    if not player_stats:
        return
    
    # Format and save CSV
    csv_data = format_and_save_csv(player_name, player_stats, stats_headers, base_directory)
    
    # Print the table
    print_table(csv_data, player_name)

if __name__ == "__main__":
    main()
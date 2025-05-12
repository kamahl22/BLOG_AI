#!/usr/bin/env python3
"""
ESPN MLB Team Stats Scraper
This script scrapes team batting, pitching, fielding statistics and team splits from ESPN.
Focused on scraping Chicago Cubs data with robust error handling and debugging.
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import time
import random
from datetime import datetime

# Set up user agent to mimic a real browser
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
    'Referer': 'https://www.espn.com/'
}

# Get the current season year
current_year = datetime.now().year

# ESPN MLB URLs
BASE_URL = "https://www.espn.com"
TEAM_URLS = {
    'team_batting': f"https://www.espn.com/mlb/stats/team/_/season/{current_year}/seasontype/2",
    'team_pitching': f"https://www.espn.com/mlb/stats/team/_/view/pitching/season/{current_year}/seasontype/2",
    'team_fielding': f"https://www.espn.com/mlb/stats/team/_/view/fielding/season/{current_year}/seasontype/2"
}
TEAM_LIST_URL = f"https://www.espn.com/mlb/teams"

def fetch_html(url):
    """Fetch HTML content from URL with retry logic"""
    max_retries = 3
    for attempt in range(max_retries):
        try:
            print(f"📡 Fetching {url}...")
            response = requests.get(url, headers=HEADERS, timeout=10)
            response.raise_for_status()
            return response.text
        except requests.exceptions.RequestException as e:
            print(f"❌ Attempt {attempt+1} failed: {e}")
            if attempt == max_retries - 1:
                print(f"❌ Failed to fetch data after {max_retries} attempts")
                return None
            time.sleep(random.uniform(2, 5))  # Random delay between retries
    return None

def parse_team_list():
    """Parse the MLB team list page to get all teams and their abbreviations"""
    html = fetch_html(TEAM_LIST_URL)
    if not html:
        return []
    
    soup = BeautifulSoup(html, 'html.parser')
    teams = []
    
    # Find all team containers
    team_containers = soup.select("div.mt7")
    
    for container in team_containers:
        league_items = container.find_all('div', class_='ContentList__Item')
        for item in league_items:
            team_link = item.find('a')
            if team_link:
                team_name = team_link.get_text(strip=True)
                team_url = team_link.get('href', '')
                # Extract team abbreviation from URL
                abbr_match = re.search(r'/team/_/name/([^/]+)', team_url)
                team_abbr = abbr_match.group(1) if abbr_match else None
                
                if team_abbr:
                    teams.append({
                        'name': team_name,
                        'abbr': team_abbr.lower(),
                        'url': f"{BASE_URL}{team_url}"
                    })
    
    print(f"Found {len(teams)} MLB teams.")
    return teams

def scrape_team_stats(stat_type):
    """Scrape team statistics for batting, pitching or fielding"""
    if stat_type not in TEAM_URLS:
        print(f"❌ Invalid stat type: {stat_type}")
        return pd.DataFrame()
    
    url = TEAM_URLS[stat_type]
    html = fetch_html(url)
    if not html:
        return pd.DataFrame()
    
    soup = BeautifulSoup(html, 'html.parser')
    
    # Debug output for testing
    print(f"🔍 Analyzing page structure for {stat_type}...")
    
    # Find the table headers and data
    try:
        # First, look for responsive tables
        print("📊 Looking for responsive tables...")
        
        # Try multiple selectors for tables - ESPN sometimes changes their HTML structure
        table_selectors = [
            '.Table__THEAD .Table__TR',             # Standard ESPN table header
            '.ResponsiveTable .Table__THEAD tr',    # Responsive table format
            'thead tr',                            # Generic table header
            '.statistics tr.stathead'              # Older ESPN statistics format
        ]
        
        header_row = None
        for selector in table_selectors:
            header_row = soup.select_one(selector)
            if header_row:
                print(f"✅ Found header with selector: {selector}")
                break
                
        if not header_row:
            print("❌ Could not find header row using standard selectors")
            # If we can't find it with specific selectors, try a more general approach
            all_tables = soup.find_all('table')
            if all_tables:
                print(f"🔍 Found {len(all_tables)} tables on the page, trying to identify the stats table...")
                for i, table in enumerate(all_tables):
                    header = table.find('thead') or table.find('tr')
                    if header:
                        print(f"✅ Using table #{i+1} as fallback")
                        header_row = header
                        break
        
        if not header_row:
            print("❌ No usable tables found. Dumping page structure for debugging...")
            print(soup.prettify()[:500] + "... [truncated]")  # Print first 500 chars for debugging
            return pd.DataFrame()
        
        # Extract headers - try different methods depending on the table structure
        if header_row.find_all('th'):
            headers = [th.get_text(strip=True) for th in header_row.find_all('th')]
        else:
            headers = [td.get_text(strip=True) for td in header_row.find_all('td')]
        
        print(f"📝 Found headers: {headers}")
        
        # Look for table body rows - try multiple selectors
        body_selectors = [
            '.Table__TBODY .Table__TR',
            '.ResponsiveTable .Table__TBODY tr',
            'tbody tr',
            '.statistics tr.oddrow, .statistics tr.evenrow'
        ]
        
        data_rows = []
        for selector in body_selectors:
            rows = soup.select(selector)
            if rows:
                print(f"✅ Found {len(rows)} data rows with selector: {selector}")
                data_rows = rows
                break
                
        if not data_rows:
            print("❌ Could not find data rows")
            return pd.DataFrame()
        
        data = []
        for row in data_rows:
            # Try to get cells as td elements
            cells = row.find_all('td')
            if not cells:
                # If no td elements, try other cell types
                cells = row.find_all(['td', 'th'])
            
            row_data = [cell.get_text(strip=True) for cell in cells]
            
            if row_data:
                # Make sure the row has the right number of columns
                if len(row_data) == len(headers):
                    data.append(row_data)
                else:
                    print(f"⚠️ Skipping row with mismatched column count: {len(row_data)} vs {len(headers)}")
        
        if not data:
            print("❌ No valid data rows found")
            return pd.DataFrame()
            
        # Create DataFrame
        df = pd.DataFrame(data, columns=headers)
        
        # Clean up column names and convert to uppercase
        df.columns = [col.upper() for col in df.columns]
        
        print(f"✅ Scraped {len(df)} teams for {stat_type}.")
        return df
    
    except Exception as e:
        print(f"❌ Error parsing {stat_type} data: {e}")
        import traceback
        print(traceback.format_exc())
        return pd.DataFrame()

def scrape_team_splits(teams):
    """Scrape team splits data for each team"""
    all_splits_data = []
    successful_teams = 0
    
    for team in teams:
        team_name = team['name']
        team_abbr = team['abbr']
        
        print(f"📊 Scraping splits for {team_name} ({team_abbr})...")
        
        # Try multiple URL patterns for splits - ESPN sometimes changes their structure
        splits_urls = [
            f"https://www.espn.com/mlb/team/splits/_/name/{team_abbr}/season/{current_year}",
            f"https://www.espn.com/mlb/team/stats/splits/_/name/{team_abbr}/season/{current_year}",
            f"https://www.espn.com/mlb/team/_/name/{team_abbr}/season/{current_year}/splits"
        ]
        
        html = None
        used_url = None
        
        # Try each URL until we get a successful response
        for url in splits_urls:
            print(f"🔍 Trying splits URL: {url}")
            temp_html = fetch_html(url)
            if temp_html:
                html = temp_html
                used_url = url
                print(f"✅ Successfully fetched data from: {url}")
                break
        
        if not html:
            print(f"❌ Failed to fetch splits data for {team_name} from any URL")
            continue
        
        soup = BeautifulSoup(html, 'html.parser')
        
        # Debug the page structure
        print(f"🔍 Analyzing page structure for splits...")
        
        # Look for split tables with multiple selectors
        table_selectors = [
            'div.Table__Title + div.Table__Scroller',
            '.ResponsiveTable',
            '.Wrapper .Table--splits',
            '.team-stats-container table',
            '.content-tab table'  # More generic fallback
        ]
        
        split_tables = []
        used_selector = None
        
        for selector in table_selectors:
            tables = soup.select(selector)
            if tables:
                split_tables = tables
                used_selector = selector
                print(f"✅ Found {len(tables)} split tables with selector: {selector}")
                break
        
        if not split_tables:
            print("❌ No split tables found. Checking for any tables...")
            
            # Last resort - find any tables in the document
            all_tables = soup.find_all('table')
            if all_tables:
                print(f"📋 Found {len(all_tables)} tables on the page, will try to identify split tables...")
                split_tables = all_tables
            else:
                # Save HTML for debugging
                with open(f"{team_abbr}_splits_debug.html", "w") as f:
                    f.write(html)
                print(f"❌ No tables found at all. Saved HTML to {team_abbr}_splits_debug.html")
                continue
        
        team_splits = []
        
        # Process each split table
        for i, table_container in enumerate(split_tables):
            print(f"📊 Processing table {i+1} of {len(split_tables)}...")
            
            # Get the table title - try multiple methods
            title_elem = None
            split_type = f"Split Type {i+1}"
            
            # Method 1: Look for a title div before the table
            if used_selector and 'Table__Title' in used_selector:
                title_elem = table_container.find_previous_sibling('div', class_='Table__Title')
                if title_elem:
                    split_type = title_elem.get_text(strip=True)
                    print(f"📑 Found split type: {split_type}")
            
            # Method 2: Look for a caption or heading nearby
            if not title_elem:
                nearby_headings = soup.select(f'h2, h3, h4, caption, .Table__Title')
                for heading in nearby_headings:
                    # Check if the heading is before the table and reasonably close
                    if heading.sourceline and table_container.sourceline and heading.sourceline < table_container.sourceline:
                        if table_container.sourceline - heading.sourceline < 10:  # Arbitrary closeness threshold
                            split_type = heading.get_text(strip=True)
                            print(f"📑 Using nearby heading as split type: {split_type}")
                            break
            
            # Find header row - try multiple selectors
            header_row = None
            header_selectors = [
                '.Table__THEAD .Table__TR',
                'thead tr',
                'tr.columnhead',
                'tr:first-child'  # Last resort
            ]
            
            for selector in header_selectors:
                if isinstance(table_container, BeautifulSoup):
                    header_row = table_container.select_one(selector)
                else:
                    header_row = table_container.select_one(selector)
                
                if header_row:
                    break
            
            if not header_row:
                print("⚠️ Could not find header row for this table, skipping...")
                continue
            
            # Extract headers
            headers = []
            header_cells = header_row.find_all(['th', 'td'])
            for cell in header_cells:
                header_text = cell.get_text(strip=True)
                headers.append(header_text if header_text else f"Column_{len(headers)}")
            
            if not headers:
                print("⚠️ No headers found in this table, skipping...")
                continue
                
            print(f"📋 Found headers: {headers}")
            
            # Find data rows - try multiple selectors
            data_selectors = [
                '.Table__TBODY .Table__TR',
                'tbody tr',
                'tr.oddrow, tr.evenrow',
                'tr:not(:first-child)'  # Last resort, excludes header
            ]
            
            data_rows = []
            for selector in data_selectors:
                if isinstance(table_container, BeautifulSoup):
                    rows = table_container.select(selector) 
                else:
                    rows = table_container.select(selector)
                
                if rows:
                    data_rows = rows
                    break
            
            if not data_rows:
                print("⚠️ No data rows found for this table")
                continue
            
            print(f"📊 Found {len(data_rows)} data rows")
            
            # Process each row
            for row in data_rows:
                row_cells = row.find_all(['td', 'th'])
                row_data = [cell.get_text(strip=True) for cell in row_cells]
                
                # Skip header-like rows or empty rows
                if not row_data or (len(row_data) == 1 and not row_data[0]):
                    continue
                
                # Skip rows with different column counts (likely headers or dividers)
                if len(row_data) != len(headers):
                    print(f"⚠️ Skipping row with mismatched column count: {len(row_data)} vs {len(headers)}")
                    continue
                
                # Create split data dictionary
                split_data = {
                    'TEAM': team_name,
                    'TEAM_ABBR': team_abbr,
                    'SPLIT_TYPE': split_type,
                    'SPLIT': row_data[0]  # Assuming first column is the split name
                }
                
                # Add all stats columns
                for j, header in enumerate(headers[1:], 1):
                    if j < len(row_data):
                        # Clean up the header name (remove spaces, special chars)
                        clean_header = re.sub(r'[^a-zA-Z0-9]', '_', header).upper()
                        clean_header = re.sub(r'_+', '_', clean_header)  # Replace multiple underscores with one
                        if not clean_header:
                            clean_header = f"STAT_{j}"
                        split_data[clean_header] = row_data[j]
                
                team_splits.append(split_data)
        
        if team_splits:
            all_splits_data.extend(team_splits)
            successful_teams += 1
            print(f"✅ Found {len(team_splits)} splits for {team_name}")
        else:
            print(f"❌ No valid splits data for {team_name}")
            # Save HTML for debugging
            with open(f"{team_abbr}_splits_debug.html", "w") as f:
                f.write(html)
            print(f"📄 Saved HTML to {team_abbr}_splits_debug.html for debugging")
    
    if all_splits_data:
        splits_df = pd.DataFrame(all_splits_data)
        print(f"✅ Scraped splits for {successful_teams} MLB teams")
        return splits_df
    else:
        print("❌ No splits data to display.")
        return pd.DataFrame()

def scrape_single_team_stats(team_abbr="chc", team_name="Chicago Cubs"):
    """Scrape stats for a single team specified by abbreviation"""
    print(f"\n📊 Focusing on {team_name} ({team_abbr.upper()})")
    
    team_data = {
        'name': team_name,
        'abbr': team_abbr.lower(),
        'url': f"https://www.espn.com/mlb/team/_/name/{team_abbr.lower()}"
    }
    
    # Create a list with just this team
    single_team = [team_data]
    
    # ===== BATTING STATS =====
    print("\n" + "="*50)
    print(f"{team_name.upper()} BATTING STATS")
    print("="*50)
    
    # Get overall team batting stats
    batting_df = scrape_team_stats('team_batting')
    if not batting_df.empty:
        # Filter for just the Cubs if we found them
        team_batting = batting_df[batting_df['TEAM'].str.contains(team_name, case=False, na=False)]
        
        if not team_batting.empty:
            print(f"\n📊 {team_name} Team Batting Stats:")
            print(team_batting)
            team_batting.to_csv(f'{team_abbr}_team_batting_{current_year}.csv', index=False)
            print(f"✅ Saved to {team_abbr}_team_batting_{current_year}.csv")
        else:
            print(f"❌ Could not find {team_name} in the batting stats table")
            # Save full table for debugging
            batting_df.to_csv(f'all_team_batting_{current_year}.csv', index=False)
            print(f"⚠️ Saved all teams to all_team_batting_{current_year}.csv for debugging")
    
    # ===== PITCHING STATS =====
    print("\n" + "="*50)
    print(f"{team_name.upper()} PITCHING STATS")
    print("="*50)
    
    pitching_df = scrape_team_stats('team_pitching')
    if not pitching_df.empty:
        team_pitching = pitching_df[pitching_df['TEAM'].str.contains(team_name, case=False, na=False)]
        
        if not team_pitching.empty:
            print(f"\n📊 {team_name} Team Pitching Stats:")
            print(team_pitching)
            team_pitching.to_csv(f'{team_abbr}_team_pitching_{current_year}.csv', index=False)
            print(f"✅ Saved to {team_abbr}_team_pitching_{current_year}.csv")
        else:
            print(f"❌ Could not find {team_name} in the pitching stats table")
            pitching_df.to_csv(f'all_team_pitching_{current_year}.csv', index=False)
            print(f"⚠️ Saved all teams to all_team_pitching_{current_year}.csv for debugging")
    
    # ===== FIELDING STATS =====
    print("\n" + "="*50)
    print(f"{team_name.upper()} FIELDING STATS")
    print("="*50)
    
    fielding_df = scrape_team_stats('team_fielding')
    if not fielding_df.empty:
        team_fielding = fielding_df[fielding_df['TEAM'].str.contains(team_name, case=False, na=False)]
        
        if not team_fielding.empty:
            print(f"\n📊 {team_name} Team Fielding Stats:")
            print(team_fielding)
            team_fielding.to_csv(f'{team_abbr}_team_fielding_{current_year}.csv', index=False)
            print(f"✅ Saved to {team_abbr}_team_fielding_{current_year}.csv")
        else:
            print(f"❌ Could not find {team_name} in the fielding stats table")
            fielding_df.to_csv(f'all_team_fielding_{current_year}.csv', index=False)
            print(f"⚠️ Saved all teams to all_team_fielding_{current_year}.csv for debugging")
    
    # ===== TEAM SPLITS =====
    print("\n" + "="*50)
    print(f"{team_name.upper()} SPLITS")
    print("="*50)
    
    splits_df = scrape_team_splits(single_team)
    if not splits_df.empty:
        print(f"\n📊 {team_name} Team Splits (sample):")
        print(splits_df.head())
        splits_df.to_csv(f'{team_abbr}_team_splits_{current_year}.csv', index=False)
        print(f"✅ Saved to {team_abbr}_team_splits_{current_year}.csv")

def main():
    """Main function to run the scraper focusing on Cubs"""
    # Just focus on Cubs for now
    scrape_single_team_stats(team_abbr="chc", team_name="Chicago Cubs")
    
    # Uncomment to get all teams
    # teams = parse_team_list()
    # if not teams:
    #     print("❌ Failed to retrieve MLB teams list.")
    #     return
    # 
    # # Scrape team batting stats
    # print("\n" + "="*50)
    # print("TEAM BATTING STATS")
    # print("="*50)
    # batting_df = scrape_team_stats('team_batting')
    # if not batting_df.empty:
    #     print("\n📊 ESPN MLB Team Batting Stats:")
    #     print(batting_df)
    #     batting_df.to_csv(f'espn_mlb_team_batting_{current_year}.csv', index=False)
    #     print(f"✅ Saved to espn_mlb_team_batting_{current_year}.csv")
    # 
    # # Scrape team pitching stats
    # print("\n" + "="*50)
    # print("TEAM PITCHING STATS")
    # print("="*50)
    # pitching_df = scrape_team_stats('team_pitching')
    # if not pitching_df.empty:
    #     print("\n📊 ESPN MLB Team Pitching Stats:")
    #     print(pitching_df)
    #     pitching_df.to_csv(f'espn_mlb_team_pitching_{current_year}.csv', index=False)
    #     print(f"✅ Saved to espn_mlb_team_pitching_{current_year}.csv")
    # 
    # # Scrape team fielding stats
    # print("\n" + "="*50)
    # print("TEAM FIELDING STATS")
    # print("="*50)
    # fielding_df = scrape_team_stats('team_fielding')
    # if not fielding_df.empty:
    #     print("\n📊 ESPN MLB Team Fielding Stats:")
    #     print(fielding_df)
    #     fielding_df.to_csv(f'espn_mlb_team_fielding_{current_year}.csv', index=False)
    #     print(f"✅ Saved to espn_mlb_team_fielding_{current_year}.csv")
    # 
    # # Scrape team splits
    # print("\n" + "="*50)
    # print("TEAM SPLITS")
    # print("="*50)
    # splits_df = scrape_team_splits(teams)
    # if not splits_df.empty:
    #     print("\n📊 ESPN MLB Team Splits (sample):")
    #     print(splits_df.head())
    #     splits_df.to_csv(f'espn_mlb_team_splits_{current_year}.csv', index=False)
    #     print(f"✅ Saved to espn_mlb_team_splits_{current_year}.csv")

if __name__ == "__main__":
    main()
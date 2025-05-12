#!/usr/bin/env python3
# BLOG_AI/sql/espn/mlb/scrape_espn_mlb_team_splits.py

import requests
from bs4 import BeautifulSoup
import json
import pandas as pd
from datetime import datetime
import os
import time

def get_team_ids():
    """Get team IDs from ESPN"""
    url = "https://www.espn.com/mlb/teams"
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"❌ Failed to fetch ESPN teams page: {e}")
        return {}

    soup = BeautifulSoup(response.text, "html.parser")
    
    team_links = soup.select(".ContentList__Item a[href*='/team/_/name/']")
    team_dict = {}
    
    for link in team_links:
        href = link.get('href', '')
        if '/team/_/name/' in href:
            team_id = href.split('/name/')[1].split('/')[0]
            team_name = link.select_one('.db').text if link.select_one('.db') else "Unknown"
            team_dict[team_id] = team_name
    
    return team_dict

def scrape_team_splits(team_id, team_name):
    """Scrape splits data for a specific team"""
    url = f"https://www.espn.com/mlb/team/splits/_/name/{team_id}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"❌ Failed to fetch splits for {team_name}: {e}")
        return None

    soup = BeautifulSoup(response.text, "html.parser")
    
    # Find all split tables
    split_tables = soup.select(".Table--fixed-left")
    
    if not split_tables:
        print(f"❌ No split tables found for {team_name}")
        return None
    
    all_splits = {}
    
    # Process each table
    for table in split_tables:
        # Find the table caption/header
        caption = table.find_previous('div', class_='Table__Title')
        if not caption:
            continue
            
        split_category = caption.text.strip()
        
        # Get headers
        headers = [th.text.strip() for th in table.select('.Table__THEAD th')]
        if not headers:
            continue
            
        # Get rows
        rows = table.select('.Table__TBODY tr')
        
        category_splits = []
        
        for row in rows:
            cols = row.select('td')
            
            # Get the split type from the first column
            if not cols:
                continue
                
            split_type = cols[0].text.strip()
            
            # Get the stats values
            stats_values = [col.text.strip() for col in cols]
            
            if len(stats_values) == len(headers):
                split_data = dict(zip(headers, stats_values))
                category_splits.append({
                    "split_type": split_type,
                    "stats": split_data
                })
        
        if category_splits:
            all_splits[split_category] = category_splits
    
    if not all_splits:
        print(f"❌ No splits data found for {team_name}")
        return None
    
    return {
        "team_id": team_id,
        "team_name": team_name,
        "data_collected_at": datetime.now().isoformat(),
        "splits": all_splits
    }

def scrape_espn_mlb_team_splits():
    print("📡 Fetching ESPN MLB team splits...")
    
    # Get team IDs
    teams = get_team_ids()
    if not teams:
        print("❌ Failed to get team IDs.")
        return False
    
    print(f"Found {len(teams)} MLB teams.")
    
    # Create directory if it doesn't exist
    os.makedirs('data/mlb/team_splits', exist_ok=True)
    
    # Process each team
    all_team_splits = []
    
    for team_id, team_name in teams.items():
        print(f"📊 Scraping splits for {team_name} ({team_id})...")
        team_splits = scrape_team_splits(team_id, team_name)
        
        if team_splits:
            all_team_splits.append(team_splits)
            
            # Save team splits to a JSON file
            file_name = f"{team_id}_{team_name.replace(' ', '_').lower()}_splits.json"
            file_path = f"data/mlb/team_splits/{file_name}"
            
            with open(file_path, 'w') as f:
                json.dump(team_splits, f, indent=2)
            
            print(f"💾 Saved {team_name}'s splits to {file_path}")
            
            # Add a small delay to avoid rate limiting
            time.sleep(1)
    
    print(f"✅ Scraped splits for {len(all_team_splits)} MLB teams")
    return all_team_splits

if __name__ == "__main__":
    team_splits = scrape_espn_mlb_team_splits()
    
    if team_splits:
        # Display a summary
        print("\n📊 ESPN MLB Team Splits Summary:\n")
        summary_data = []
        
        for team in team_splits:
            split_categories = list(team["splits"].keys())
            num_categories = len(split_categories)
            
            total_splits = sum(len(splits) for splits in team["splits"].values())
            
            summary_data.append({
                "Team": team["team_name"],
                "Split Categories": num_categories,
                "Total Split Types": total_splits
            })
        
        summary_df = pd.DataFrame(summary_data)
        print(summary_df.to_string(index=False))
    else:
        print("❌ No splits data to display.")
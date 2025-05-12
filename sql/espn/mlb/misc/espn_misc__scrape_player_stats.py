#!/usr/bin/env python3
# BLOG_AI/sql/espn/mlb/scrape_espn_mlb_player_stats.py

import requests
from bs4 import BeautifulSoup
import json
import pandas as pd
from datetime import datetime
import os
import time
import re

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

def extract_player_id(url):
    """Extract player ID from URL"""
    if not url:
        return None
    
    # Try to match player ID pattern
    match = re.search(r'/id/(\d+)/', url)
    return match.group(1) if match else None

def scrape_team_batting_stats(team_id, team_name):
    """Scrape batting stats for all players on a team"""
    url = f"https://www.espn.com/mlb/team/stats/_/name/{team_id}/table/batting/sort/atBats/dir/desc"
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"❌ Failed to fetch batting stats for {team_name}: {e}")
        return None

    soup = BeautifulSoup(response.text, "html.parser")
    
    # Find the stats table
    stats_table = soup.select_one('.Table__TBODY')
    if not stats_table:
        print(f"❌ Could not find the batting stats table for {team_name}")
        return None
    
    # Get headers
    header_elements = soup.select('.Table__THEAD .Table__TR th')
    headers = [header.text.strip() for header in header_elements]
    
    if not headers:
        print(f"❌ Could not find headers for {team_name} batting stats")
        return None
    
    # Get rows
    rows = stats_table.select('tr')
    
    players = []
    
    for row in rows:
        # Skip header/total rows
        if 'Table__even' in row.get('class', []) or 'Table__TR--sm' in row.get('class', []):
            continue
            
        cols = row.select('td')
        
        # Check if it's a player row (has a name)
        name_cell = row.select_one('td:first-child a')
        if not name_cell:
            continue
            
        player_name = name_cell.text.strip()
        player_link = name_cell.get('href', '')
        player_id = extract_player_id(player_link)
        
        # Get position if available
        position_cell = row.select_one('td:nth-child(2)')
        position = position_cell.text.strip() if position_cell else ""
        
        # Get stats values
        stats_values = [col.text.strip() for col in cols]
        
        # Create player data dictionary
        player_data = {
            "player_id": player_id,
            "player_name": player_name,
            "position": position,
            "stats": dict(zip(headers, stats_values))  # Map stat name to value
        }
        
        players.append(player_data)
    
    return players

def scrape_team_pitching_stats(team_id, team_name):
    """Scrape pitching stats for all players on a team"""
    url = f"https://www.espn.com/mlb/team/stats/_/name/{team_id}/table/pitching/sort/inningsPitched/dir/desc"
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"❌ Failed to fetch pitching stats for {team_name}: {e}")
        return None

    soup = BeautifulSoup(response.text, "html.parser")
    
    # Find the stats table
    stats_table = soup.select_one('.Table__TBODY')
    if not stats_table:
        print(f"❌ Could not find the pitching stats table for {team_name}")
        return None
    
    # Get headers
    header_elements = soup.select('.Table__THEAD .Table__TR th')
    headers = [header.text.strip() for header in header_elements]
    
    if not headers:
        print(f"❌ Could not find headers for {team_name} pitching stats")
        return None
    
    # Get rows
    rows = stats_table.select('tr')
    
    pitchers = []
    
    for row in rows:
        # Skip header/total rows
        if 'Table__even' in row.get('class', []) or 'Table__TR--sm' in row.get('class', []):
            continue
            
        cols = row.select('td')
        
        # Check if it's a player row (has a name)
        name_cell = row.select_one('td:first-child a')
        if not name_cell:
            continue
            
        player_name = name_cell.text.strip()
        player_link = name_cell.get('href', '')
        player_id = extract_player_id(player_link)
        
        # Get position - should be P for pitchers
        position = "P"
        
        # Get stats values
        stats_values = [col.text.strip() for col in cols]
        
        # Create player data dictionary
        player_data = {
            "player_id": player_id,
            "player_name": player_name,
            "position": position,
            "stats": dict(zip(headers, stats_values))  # Map stat name to value
        }
        
        pitchers.append(player_data)
    
    return pitchers

def scrape_espn_mlb_player_stats():
    print("📡 Fetching ESPN MLB player stats...")
    
    # Get team IDs
    teams = get_team_ids()
    if not teams:
        print("❌ Failed to get team IDs.")
        return False
    
    print(f"Found {len(teams)} MLB teams.")
    
    # Create directories if they don't exist
    os.makedirs('data/mlb/player_stats/batting', exist_ok=True)
    os.makedirs('data/mlb/player_stats/pitching', exist_ok=True)
    
    all_teams_data = []
    
    for team_id, team_name in teams.items():
        print(f"📊 Scraping player stats for {team_name} ({team_id})...")
        
        # Scrape batting stats
        batters = scrape_team_batting_stats(team_id, team_name)
        if batters:
            print(f"⚾ Found {len(batters)} batters for {team_name}")
            
            # Save batting stats to JSON
            team_file_name = team_name.replace(' ', '_').lower()
            batting_file_path = f"data/mlb/player_stats/batting/{team_id}_{team_file_name}_batting.json"
            
            batting_data = {
                "team_id": team_id,
                "team_name": team_name,
                "data_collected_at": datetime.now().isoformat(),
                "players": batters
            }
            
            with open(batting_file_path, 'w') as f:
                json.dump(batting_data, f, indent=2)
            
            print(f"💾 Saved {team_name}'s batting stats to {batting_file_path}")
        
        # Scrape pitching stats
        pitchers = scrape_team_pitching_stats(team_id, team_name)
        if pitchers:
            print(f"⚾ Found {len(pitchers)} pitchers for {team_name}")
            
            # Save pitching stats to JSON
            team_file_name = team_name.replace(' ', '_').lower()
            pitching_file_path = f"data/mlb/player_stats/pitching/{team_id}_{team_file_name}_pitching.json"
            
            pitching_data = {
                "team_id": team_id,
                "team_name": team_name,
                "data_collected_at": datetime.now().isoformat(),
                "players": pitchers
            }
            
            with open(pitching_file_path, 'w') as f:
                json.dump(pitching_data, f, indent=2)
            
            print(f"💾 Saved {team_name}'s pitching stats to {pitching_file_path}")
        
        # Combine both for team data
        team_data = {
            "team_id": team_id,
            "team_name": team_name,
            "batters": batters if batters else [],
            "pitchers": pitchers if pitchers else []
        }
        
        all_teams_data.append(team_data)
        
        # Add delay to avoid rate limiting
        time.sleep(1)
    
    # Create summary dataframe for display
    batting_counts = []
    pitching_counts = []
    
    for team in all_teams_data:
        batting_counts.append({
            "Team": team["team_name"],
            "
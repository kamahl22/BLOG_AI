import requests
import json
import os
import csv
from datetime import datetime
from dateutil import parser
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

player_id = "36040"
player_name = "Lourdes Gurriel Jr."
team_id = "29"
team_name = "Arizona Diamondbacks"
season = 2025

# Stat mapping
STAT_MAPPING = [
    ("AB", "At Bats"),
    ("R", "Runs"),
    ("H", "Hits"),
    ("2B", "Doubles"),
    ("3B", "Triples"),
    ("HR", "Home Runs"),
    ("RBI", "Runs Batted In"),
    ("BB", "Walks"),
    ("HBP", "Hit By Pitch"),
    ("SO", "Strikeouts"),
    ("SB", "Stolen Bases"),
    ("CS", "Caught Stealing"),
    ("AVG", "Batting Average"),
    ("OBP", "On Base Percentage"),
    ("SLG", "Slugging Percentage"),
    ("OPS", "OPS")
]

# API URL
url = f"https://site.web.api.espn.com/apis/common/v3/sports/baseball/mlb/athletes/36040/gamelog?season={season}"

# Function to extract opponent information
def get_opponent_info(event):
    try:
        opponent_obj = event.get('opponent', {})
        opponent_name = opponent_obj.get('displayName', 'Unknown')
        return opponent_name
    except Exception as e:
        logger.error(f"Error extracting opponent for event {event.get('id', 'Unknown')}: {e}")
        return 'Unknown'

# Function to parse date
def parse_date(raw_date):
    if not raw_date:
        return 'N/A'
    try:
        return parser.parse(raw_date).strftime("%Y-%m-%d")
    except Exception as e:
        logger.error(f"Date parsing failed for {raw_date}: {e}")
        return 'N/A'

# Function to get game result
def get_game_result(event):
    try:
        home_score = event.get('homeTeamScore')
        away_score = event.get('awayTeamScore')
        home_team_id = event.get('homeTeamId')
        
        if home_score is not None and away_score is not None:
            if home_team_id == team_id:  # Team is home team
                result = 'W' if int(home_score) > int(away_score) else 'L'
                return f"{result} {home_score}-{away_score}"
            else:  # Team is away team
                result = 'W' if int(away_score) > int(home_score) else 'L'
                return f"{result} {away_score}-{home_score}"
        return 'N/A'
    except Exception as e:
        logger.error(f"Error extracting result for event {event.get('id', 'Unknown')}: {e}")
        return 'N/A'

# Fetch data from API
logger.info(f"Fetching gamelog data for {player_name} ID {player_id}, season {season}")
response = requests.get(url)
if response.status_code == 200:
    data = response.json()
    logger.info("Successfully fetched data from API")
    
    # Save raw API response for debugging
    output_dir = "/Users/kamahl/BLOG_AI/espn/mlb/arizona-diamondbacks/lourdes_gurriel_jr"
    os.makedirs(output_dir, exist_ok=True)
    with open(os.path.join(output_dir, f"raw_response_{player_id}_{season}.json"), 'w') as f:
        json.dump(data, f, indent=2)
else:
    logger.error(f"API request failed with status {response.status_code}")
    print(f"Error: {response.status_code}")
    exit()

# Store problematic games for debugging
problematic_games = {}

# Prepare CSV data
csv_headers = ["Season", "Month", "Date", "Teams", "Result"] + [stat[1] for stat in STAT_MAPPING]
csv_data = []

# Initialize season name
season_name = str(season)
season_display_name = season_name

# Check if seasonTypes exists
if 'seasonTypes' in data:
    for season_type in data.get('seasonTypes', []):
        season_display_name = season_type.get('displayName', season_name)
        
# Process game-by-game stats
print(f"\n{'='*60}")
print(f"Season: {season_display_name}")
print(f"{'='*60}")

# First method: Check if we have events directly in the data
games_processed = False
events_dict = data.get('events', {})
if events_dict:
    games_processed = True
    for game_id, event in events_dict.items():
        # Extract game data
        game_date = parse_date(event.get('gameDate', 'N/A'))
        month = 'Unknown'
        if game_date != 'N/A':
            try:
                month = datetime.strptime(game_date, "%Y-%m-%d").strftime("%B")
            except ValueError:
                logger.warning(f"Could not parse month from date {game_date}")
        
        print(f"\nMonth: {month}")
        print(f"{'-'*40}")
        
        # Get opponent
        opponent_name = get_opponent_info(event)
        
        # Extract home/away indicator
        at_vs = event.get('atVs', 'vs')
        
        # Full team matchup
        matchup = f"{team_name} {at_vs} {opponent_name}"
        
        # Extract result
        game_result = get_game_result(event)
        
        # Print relevant information
        print(f"Teams: {matchup}")
        print(f"Date: {game_date}")
        print(f"Result: {game_result}")
        
        # Get stats 
        stats = []
        if 'stats' in event:
            stats = event.get('stats', [])
        else:
            # Try to look for stats in the 'categories' structure
            event_id = event.get('id', game_id)
            if 'seasonTypes' in data:
                for season_type in data.get('seasonTypes', []):
                    for category in season_type.get('categories', []):
                        if category.get('type') == 'event':
                            for evt in category.get('events', []):
                                if evt.get('eventId') == event_id:
                                    stats = evt.get('stats', [])
                                    break
        
        # Create CSV row
        csv_row = {
            "Season": season_display_name,
            "Month": month,
            "Date": game_date,
            "Teams": matchup,
            "Result": game_result
        }
        
        # Add stats to the row
        for i, (abbrev, name) in enumerate(STAT_MAPPING):
            value = stats[i] if i < len(stats) else 'N/A'
            print(f"  {name:<20}: {value}")
            csv_row[name] = value
        
        # Log problematic games
        if opponent_name == "Unknown" or game_date == "N/A" or game_result == "N/A" or len(stats) == 0:
            problematic_games[game_id] = {"event": event, "stats_found": len(stats) > 0}
        
        csv_data.append(csv_row)
        print()

# Second method: If no events were processed, try the seasonTypes structure
if not games_processed and 'seasonTypes' in data:
    for season_type in data.get('seasonTypes', []):
        season_display_name = season_type.get('displayName', season_name)
        
        for category in season_type.get('categories', []):
            if category.get('type') == 'event':
                month = category.get('displayName', 'Unknown').capitalize()
                print(f"\nMonth: {month}")
                print(f"{'-'*40}")
                
                for event in category.get('events', []):
                    game_id = event.get('eventId', 'Unknown')
                    
                    # Look for corresponding event in the events dictionary if it exists
                    event_details = data.get('events', {}).get(game_id, {})
                    
                    # Get opponent
                    opponent_name = 'Unknown'
                    if event_details:
                        opponent_name = get_opponent_info(event_details)
                    else:
                        opponent_name = get_opponent_info(event)
                    
                    # Extract home/away indicator
                    at_vs = event.get('atVs', event_details.get('atVs', 'vs'))
                    
                    # Full team matchup
                    matchup = f"{team_name} {at_vs} {opponent_name}"
                    
                    # Extract date
                    raw_date = event.get('gameDate', event_details.get('gameDate', 'N/A'))
                    game_date = parse_date(raw_date)
                    
                    # Extract result
                    game_result = 'N/A'
                    if event_details:
                        game_result = get_game_result(event_details)
                    else:
                        game_result = get_game_result(event)
                    
                    # Print relevant information
                    print(f"Teams: {matchup}")
                    print(f"Date: {game_date}")
                    print(f"Result: {game_result}")
                    
                    # Get stats
                    stats = event.get('stats', [])
                    
                    # Create CSV row
                    csv_row = {
                        "Season": season_display_name,
                        "Month": month,
                        "Date": game_date,
                        "Teams": matchup,
                        "Result": game_result
                    }
                    
                    # Add stats to the row
                    for i, (abbrev, name) in enumerate(STAT_MAPPING):
                        value = stats[i] if i < len(stats) else 'N/A'
                        print(f"  {name:<20}: {value}")
                        csv_row[name] = value
                    
                    # Log problematic games
                    if opponent_name == "Unknown" or game_date == "N/A" or game_result == "N/A":
                        problematic_games[game_id] = {"event": event, "stats_found": len(stats) > 0}
                    
                    csv_data.append(csv_row)
                    print()

# Process season summary stats
summary_stats = []
if 'summary' in data and 'stats' in data['summary']:
    summary_stats = data['summary'].get('stats', [])
elif 'seasonTypes' in data:
    for season_type in data.get('seasonTypes', []):
        summary = data.get('summary', {}).get('stats', [])
        for stat_group in summary:
            if stat_group.get('type') == 'total':
                summary_stats = stat_group.get('stats', [])
                break

if summary_stats:
    print(f"\n{'='*60}")
    print("Season Totals")
    print(f"{'='*60}")
    
    csv_row = {
        "Season": season_display_name,
        "Month": "Total",
        "Date": "N/A",
        "Teams": "Season Totals",
        "Result": "N/A"
    }
    
    for i, (abbrev, name) in enumerate(STAT_MAPPING):
        value = summary_stats[i] if i < len(summary_stats) else 'N/A'
        print(f"  {name:<20}: {value}")
        csv_row[name] = value
    
    csv_data.append(csv_row)

# Write to CSV
output_file = os.path.join(output_dir, f"lourdes_gurriel_jr_gamelog.csv")
if csv_data:
    with open(output_file, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=csv_headers)
        writer.writeheader()
        for row in csv_data:
            writer.writerow(row)
    
    print(f"\nCSV file saved to: {output_file}")
else:
    logger.warning("No data was processed. CSV was not created.")

# Save problematic games for debugging
debug_file = os.path.join(output_dir, f"debug_player_{player_id}_{season}.json")
if problematic_games:
    print(f"\nFound {len(problematic_games)} games with missing or incomplete data.")
    print(f"Writing debug data to {debug_file}")
    with open(debug_file, 'w') as f:
        json.dump(problematic_games, f, indent=2)

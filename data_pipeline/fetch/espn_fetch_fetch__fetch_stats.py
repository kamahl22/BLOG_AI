import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from fetch_supabase import insert_player_stats
from dotenv import load_dotenv
from supabase import create_client
import logging

logging.basicConfig(
    level=logging.DEBUG,
    filename='data_pipeline/pipeline.log',
    format='%(asctime)s - %(levelname)s - %(message)s',
    filemode='a'
)
logger = logging.getLogger(__name__)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
console_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logger.addHandler(console_handler)

PLAYERS = [{'id': '33192', 'name': 'Aaron Judge', 'team': 'New York Yankees'}]

def validate_schema():
    """Validate player_stats schema."""
    logger.info("Validating player_stats schema")
    try:
        supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_KEY'))
        schema = supabase.table('player_stats').select('season,games,batting_avg').limit(1).execute()
        logger.info("player_stats schema validated")
        return True
    except Exception as e:
        logger.error(f"player_stats schema validation failed: {e}")
        return False

def fetch_espn_player_stats(player_id, player_name, team_name):
    """Fetches player stats from ESPN."""
    logger.info(f"Fetching stats for {player_name}")
    if not validate_schema():
        logger.error("Skipping fetch due to schema validation failure")
        return None

    url = f"https://www.espn.com/mlb/player/stats/_/id/{player_id}"
    try:
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
        logger.debug(f"ESPN stats response status: {response.status_code}")
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        stats = {
            'sport': 'MLB',
            'player_name': player_name,
            'team_name': team_name,
            'stat_type': 'batting',
            'season': 2025,
            'games': 0,
            'at_bats': 0,
            'runs': 0,
            'hits': 0,
            'doubles': 0,
            'triples': 0,
            'home_runs': 0,
            'rbi': 0,
            'walks': 0,
            'strikeouts': 0,
            'stolen_bases': 0,
            'caught_stealing': 0,
            'batting_avg': 0.0,
            'on_base_pct': 0.0,
            'slugging_pct': 0.0,
            'ops': 0.0,
            'source': 'ESPN',
            'stat_date': datetime.now().strftime('%Y-%m-%d')
        }

        table = soup.find('table', class_='Table')
        if table:
            logger.debug(f"Found stats table for {player_name}")
            rows = table.find_all('tr')
            for row in rows[1:]:
                cols = row.find_all('td')
                if len(cols) >= 16:
                    try:
                        stats['games'] = int(cols[0].text) if cols[0].text else 0
                        stats['at_bats'] = int(cols[1].text) if cols[1].text else 0
                        stats['runs'] = int(cols[2].text) if cols[2].text else 0
                        stats['hits'] = int(cols[3].text) if cols[3].text else 0
                        stats['doubles'] = int(cols[4].text) if cols[4].text else 0
                        stats['triples'] = int(cols[5].text) if cols[5].text else 0
                        stats['home_runs'] = int(cols[6].text) if cols[6].text else 0
                        stats['rbi'] = int(cols[7].text) if cols[7].text else 0
                        stats['walks'] = int(cols[8].text) if cols[8].text else 0
                        stats['strikeouts'] = int(cols[9].text) if cols[9].text else 0
                        stats['stolen_bases'] = int(cols[10].text) if cols[10].text else 0
                        stats['caught_stealing'] = int(cols[11].text) if cols[11].text else 0
                        stats['batting_avg'] = float(cols[12].text) if cols[12].text else 0.0
                        stats['on_base_pct'] = float(cols[13].text) if cols[13].text else 0.0
                        stats['slugging_pct'] = float(cols[14].text) if cols[14].text else 0.0
                        stats['ops'] = float(cols[15].text) if cols[15].text else 0.0
                    except ValueError:
                        logger.warning(f"Invalid value in stats for {player_name}")
        else:
            logger.warning(f"No stats table found for {player_name}")

        result = insert_player_stats(stats)
        if result['success']:
            logger.info(f"Inserted player stats for {player_name}: {stats}")
        else:
            logger.error(f"Failed to insert player stats for {player_name}: {result['error']}")
        return stats
    except Exception as e:
        logger.error(f"Error fetching player stats for {player_name}: {e}")
        return None

def fetch_all_player_stats():
    """Fetches stats for all players."""
    logger.info("Starting player stats collection")
    for player in PLAYERS:
        fetch_espn_player_stats(player['id'], player['name'], player['team'])
    logger.info("Completed player stats collection")

if __name__ == "__main__":
    fetch_all_player_stats()
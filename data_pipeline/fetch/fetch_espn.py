import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from fetch_supabase import insert_player_splits
import logging

logging.basicConfig(level=logging.INFO, filename='data_pipeline/pipeline.log', format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def fetch_espn_player_splits(player_id, player_name, team_name):
    url = f"https://www.espn.com/mlb/player/splits/_/id/{player_id}"
    try:
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find splits table (adjust based on ESPN HTML)
        table = soup.find('table', class_='Table')
        if not table:
            logger.error(f"No splits table found for player {player_id}")
            return None
            
        splits_data = {
            'sport': 'MLB',
            'player_name': player_name,
            'team_name': team_name,
            'split_type': 'vs_left',
            'split_value': 'vs. Left',
            'season': 2025,
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
        
        # Parse splits (update based on ESPN HTML)
        rows = table.find_all('tr')
        for row in rows[1:]:
            cols = row.find_all('td')
            if len(cols) > 5 and 'Left' in cols[0].text:
                try:
                    splits_data['at_bats'] = int(cols[1].text)
                    splits_data['hits'] = int(cols[2].text)
                    splits_data['batting_avg'] = float(cols[3].text)
                    # Add more mappings
                except ValueError:
                    continue
        
        result = insert_player_splits(splits_data)
        if result['success']:
            logger.info(f"Inserted splits for {player_name}")
        else:
            logger.error(f"Failed to insert splits for {player_name}: {result['error']}")
        return splits_data
    except Exception as e:
        logger.error(f"Error fetching splits for player {player_id}: {e}")
        return None

if __name__ == "__main__":
    fetch_espn_player_splits('12345', 'Jane Doe', 'Testers')
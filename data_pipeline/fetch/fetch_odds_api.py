import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
import requests
from datetime import datetime
from fetch_supabase import insert_odds_data
from dotenv import load_dotenv
import logging

logging.basicConfig(level=logging.INFO, filename='data_pipeline/pipeline.log', format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

load_dotenv()
ODDS_API_KEY = os.getenv('ODDS_API_KEY')

def fetch_odds_data():
    url = f"https://api.the-odds-api.com/v4/sports/baseball_mlb/odds/?apiKey={ODDS_API_KEY}&regions=us&markets=h2h"
    try:
        response = requests.get(url)
        response.raise_for_status()
        games = response.json()
        
        for game in games:
            home_team = game['home_team']
            away_team = game['away_team']
            odds = game.get('bookmakers', [])[0].get('markets', [])[0].get('outcomes', [])
            home_odds = next((o['price'] for o in odds if o['name'] == home_team), None)
            away_odds = next((o['price'] for o in odds if o['name'] == away_team), None)
            
            if home_odds and away_odds:
                data = {
                    'sport': 'MLB',
                    'home_team': home_team,
                    'away_team': away_team,
                    'home_odds': int(home_odds),
                    'away_odds': int(away_odds),
                    'game_date': datetime.now().strftime('%Y-%m-%d')
                }
                result = insert_odds_data(data)
                if result['success']:
                    logger.info(f"Inserted odds for {home_team} vs {away_team}")
                else:
                    logger.error(f"Failed to insert odds: {result['error']}")
    except Exception as e:
        logger.error(f"Error fetching odds data: {e}")

if __name__ == "__main__":
    fetch_odds_data()
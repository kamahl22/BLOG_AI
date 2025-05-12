import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
import requests
from datetime import datetime
from fetch_supabase import insert_odds_data
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

load_dotenv()
ODDS_API_KEY = os.getenv('ODDS_API_KEY')

def validate_schema():
    """Validate odds_data schema."""
    logger.info("Validating odds_data schema")
    try:
        supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_KEY'))
        schema = supabase.table('odds_data').select('home_odds,away_odds').limit(1).execute()
        logger.info("odds_data schema validated")
        return True
    except Exception as e:
        logger.error(f"odds_data schema validation failed: {e}")
        return False

def fetch_odds_data():
    """Fetches MLB odds from The Odds API."""
    logger.info("Fetching odds data")
    if not ODDS_API_KEY:
        logger.error("ODDS_API_KEY not set")
        return
    if not validate_schema():
        logger.error("Skipping fetch due to schema validation failure")
        return

    url = f"https://api.the-odds-api.com/v4/sports/baseball_mlb/odds/?apiKey={ODDS_API_KEY}®ions=us&markets=h2h"
    try:
        response = requests.get(url, timeout=10)
        logger.debug(f"The Odds API response status: {response.status_code}")
        response.raise_for_status()
        games = response.json()

        if not games:
            logger.warning("No games found")
            return

        for game in games:
            home_team = game.get('home_team')
            away_team = game.get('away_team')
            bookmakers = game.get('bookmakers', [])
            if not bookmakers:
                logger.warning(f"No bookmakers for {home_team} vs {away_team}")
                continue

            odds = bookmakers[0].get('markets', [])[0].get('outcomes', [])
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
                    logger.info(f"Inserted odds for {home_team} vs {away_team}: {data}")
                else:
                    logger.error(f"Failed to insert odds: {result['error']}")
            else:
                logger.warning(f"Missing odds for {home_team} vs {away_team}")
    except Exception as e:
        logger.error(f"Error fetching odds data: {e}")

if __name__ == "__main__":
    fetch_odds_data()
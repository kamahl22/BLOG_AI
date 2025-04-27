import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
import requests
from dotenv import load_dotenv
from data_pipeline.fetch.fetch_supabase import insert_odds_data
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, filename='data_pipeline/pipeline.log')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()
ODDS_API_KEY = os.getenv('ODDS_API_KEY')
BASE_URL = 'https://api.the-odds-api.com/v4/sports'

# Supported sports with their Odds API keys
SPORTS = {
    'NFL': 'americanfootball_nfl',
    'NBA': 'basketball_nba',
    'MLB': 'baseball_mlb',
    'NCAAF': 'americanfootball_ncaaf',
    'NCAAMB': 'basketball_ncaam',
    'NCAAWB': 'basketball_ncaaw',
    'NHL': 'icehockey_nhl',
    'SOCCER': 'soccer_epl'
}

def fetch_odds(sport_key=None):
    """
    Fetches odds from The Odds API for all sports or a specific sport.
    Args:
        sport_key (str, optional): The Odds API sport key (e.g., 'americanfootball_nfl').
                                   If None, fetches for all SPORTS.
    Returns:
        list: Aggregated odds data for the specified sport(s).
    """
    odds_data = []
    sports_to_fetch = [sport_key] if sport_key else SPORTS.values()

    for sport in sports_to_fetch:
        try:
            url = f"{BASE_URL}/{sport}/odds"
            params = {'apiKey': ODDS_API_KEY, 'regions': 'us', 'markets': 'h2h'}
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()

            if not data:
                logger.warning(f"No games found for {sport}")
                continue

            # Process and format data for Supabase
            for game in data:
                # Check if required fields exist
                bookmakers = game.get('bookmakers', [])
                if not bookmakers:
                    logger.warning(f"No bookmakers for game {game.get('id')} in {sport}")
                    continue

                markets = bookmakers[0].get('markets', [])
                if not markets:
                    logger.warning(f"No markets for game {game.get('id')} in {sport}")
                    continue

                outcomes = markets[0].get('outcomes', [])
                if not outcomes:
                    logger.warning(f"No outcomes for game {game.get('id')} in {sport}")
                    continue

                # Extract odds (use first outcome; adjust if needed for both teams)
                formatted_game = {
                    'sport': next((k for k, v in SPORTS.items() if v == sport), sport),
                    'home_team': game.get('home_team'),
                    'away_team': game.get('away_team'),
                    'moneyline_odds': outcomes[0].get('price'),
                    'game_date': game.get('commence_time')
                }

                # Validate required fields
                if not all([formatted_game['home_team'], formatted_game['away_team'], formatted_game['moneyline_odds']]):
                    logger.warning(f"Invalid game data for {game.get('id')} in {sport}: {formatted_game}")
                    continue

                odds_data.append(formatted_game)
                insert_odds_data(formatted_game)
            logger.info(f"Successfully fetched {len(data)} games for {sport}")

        except requests.RequestException as e:
            logger.error(f"Error fetching odds for {sport}: {e}")
            continue

    return odds_data

if __name__ == '__main__':
    # Fetch odds for all sports
    all_odds = fetch_odds()
    print(f"Fetched {len(all_odds)} games across all sports")
    
    # Test specific sport (e.g., NFL)
    nfl_odds = fetch_odds(sport_key='americanfootball_nfl')
    print(f"Fetched {len(nfl_odds)} NFL games")
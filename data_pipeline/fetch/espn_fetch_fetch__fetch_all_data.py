import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from fetch_teamrankings import fetch_all_team_stats
from fetch_odds_api import fetch_odds_data
from fetch_espn_stats import fetch_all_player_stats
from fetch_espn_splits import fetch_all_player_splits
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

def fetch_all_mlb_data():
    """Fetches all MLB data."""
    logger.info("Starting MLB data collection")
    try:
        fetch_all_team_stats()
        fetch_odds_data()
        fetch_all_player_stats()
        fetch_all_player_splits()
        logger.info("Completed MLB data collection")
    except Exception as e:
        logger.error(f"Error in data collection: {e}")
        raise

if __name__ == "__main__":
    fetch_all_mlb_data()
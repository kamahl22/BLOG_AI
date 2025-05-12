import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from fetch_supabase import insert_team_stats
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

MLB_TEAMS = ['chicago-cubs']

def validate_schema():
    """Validate team_stats schema."""
    logger.info("Validating team_stats schema")
    load_dotenv()
    try:
        supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_KEY'))
        schema = supabase.table('team_stats').select('season,games,batting_avg').limit(1).execute()
        logger.info("team_stats schema validated")
        return True
    except Exception as e:
        logger.error(f"team_stats schema validation failed: {e}")
        return False

def fetch_teamrankings_team_stats(team_slug):
    """Fetches team stats from TeamRankings."""
    logger.info(f"Fetching stats for {team_slug}")
    if not validate_schema():
        logger.error("Skipping fetch due to schema validation failure")
        return None

    url = f"https://www.teamrankings.com/mlb/team/{team_slug}/stats"
    try:
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
        logger.debug(f"TeamRankings response status: {response.status_code}")
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        stats = {
            'sport': 'MLB',
            'team_name': team_slug.replace('-', ' ').title(),
            'stat_type': 'season_stats',
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
            'batting_avg': 0.0,
            'on_base_pct': 0.0,
            'slugging_pct': 0.0,
            'ops': 0.0,
            'run_line_wins': 0,
            'run_line_losses': 0,
            'run_line_cover_pct': 0.0,
            'source': 'TeamRankings',
            'stat_date': datetime.now().strftime('%Y-%m-%d')
        }

        table = soup.find('table', class_='tr-table')
        if table:
            logger.debug(f"Found stats table for {team_slug}")
            rows = table.find_all('tr')
            for row in rows[1:]:
                cols = row.find_all('td')
                if len(cols) >= 2:
                    stat_name = cols[0].text.strip().lower()
                    stat_value = cols[1].text.strip()
                    try:
                        if 'games played' in stat_name:
                            stats['games'] = int(stat_value)
                        elif 'at bats' in stat_name:
                            stats['at_bats'] = int(stat_value)
                        elif 'batting avg' in stat_name:
                            stats['batting_avg'] = float(stat_value)
                    except ValueError:
                        logger.warning(f"Invalid value for {stat_name}: {stat_value}")
        else:
            logger.warning(f"No stats table found for {team_slug}")

        result = insert_team_stats(stats)
        if result['success']:
            logger.info(f"Inserted team stats for {team_slug}: {stats}")
        else:
            logger.error(f"Failed to insert team stats for {team_slug}: {result['error']}")
        return stats
    except Exception as e:
        logger.error(f"Error fetching team stats for {team_slug}: {e}")
        return None

def fetch_all_team_stats():
    """Fetches stats for all MLB teams."""
    logger.info("Starting team stats collection")
    for team in MLB_TEAMS:
        fetch_teamrankings_team_stats(team)
    logger.info("Completed team stats collection")

if __name__ == "__main__":
    fetch_all_team_stats()
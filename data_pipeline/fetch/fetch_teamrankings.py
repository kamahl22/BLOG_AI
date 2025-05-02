import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from fetch_supabase import insert_team_stats
import logging

logging.basicConfig(level=logging.INFO, filename='data_pipeline/pipeline.log', format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def fetch_teamrankings_team_stats(team_slug):
    url = f"https://www.teamrankings.com/mlb/team/{team_slug}/stats"
    try:
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract team stats from relevant table
        table = soup.find('table', class_='tr-table')
        if not table:
            logger.error(f"No stats table found for {team_slug}")
            return None
            
        # Parse key stats (adjust selectors based on actual HTML)
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
        
        # Example parsing (update based on TeamRankings HTML)
        rows = table.find_all('tr')
        for row in rows[1:]:
            cols = row.find_all('td')
            if len(cols) > 1:
                stat_name = cols[0].text.strip().lower()
                stat_value = cols[1].text.strip()
                try:
                    if 'games' in stat_name:
                        stats['games'] = int(stat_value)
                    elif 'at bats' in stat_name:
                        stats['at_bats'] = int(stat_value)
                    elif 'batting avg' in stat_name:
                        stats['batting_avg'] = float(stat_value)
                    # Add more mappings
                except ValueError:
                    continue
        
        result = insert_team_stats(stats)
        if result['success']:
            logger.info(f"Successfully inserted team stats for {team_slug}")
        else:
            logger.error(f"Failed to insert team stats for {team_slug}: {result['error']}")
        return stats
    except Exception as e:
        logger.error(f"Error fetching team stats for {team_slug}: {e}")
        return None

if __name__ == "__main__":
    fetch_teamrankings_team_stats('chicago-cubs')
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv
from data_pipeline.fetch.fetch_supabase import insert_team_stats, insert_player_stats, insert_player_splits
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, filename='data_pipeline/pipeline.log')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

def fetch_teamrankings_team_stats(team_slug='chicago-cubs'):
    """
    Scrapes team stats (e.g., run line trends) from TeamRankings.
    """
    url = f"https://www.teamrankings.com/mlb/team/{team_slug}/run-line-trends"
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # Extract run line trends (simplified; adjust based on page structure)
        table = soup.find('table', class_='tr-table')
        if not table:
            logger.warning(f"No run line trends table found for {team_slug}")
            return None

        rows = table.find_all('tr')[1:]  # Skip header
        stats = {
            'sport': 'MLB',
            'team_name': 'Chicago Cubs',
            'stat_type': 'run_line_trends',
            'run_line_wins': 0,
            'run_line_losses': 0,
            'run_line_cover_pct': 0.0,
            'source': 'TeamRankings',
            'stat_date': datetime.now().date()
        }

        for row in rows:
            cols = row.find_all('td')
            if len(cols) > 2:
                stats['run_line_wins'] += int(cols[1].text) if cols[1].text.isdigit() else 0
                stats['run_line_losses'] += int(cols[2].text) if cols[2].text.isdigit() else 0
                cover_pct = cols[3].text.strip('%')
                stats['run_line_cover_pct'] = float(cover_pct) / 100 if cover_pct.replace('.', '').isdigit() else 0.0

        insert_team_stats(stats)
        logger.info(f"Fetched run line trends for {team_slug}")
        return stats
    except Exception as e:
        logger.error(f"Error fetching TeamRankings team stats for {team_slug}: {e}")
        return None

def fetch_espn_team_stats(team_abbr='chc'):
    """
    Scrapes team batting stats from ESPN.
    """
    url = f"https://www.espn.com/mlb/team/stats/_/name/{team_abbr}/chicago-cubs"
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # Extract batting stats table
        table = soup.find('table', class_='Table')
        if not table:
            logger.warning(f"No batting stats table found for {team_abbr}")
            return None

        df = pd.read_html(str(table))[0]
        stats = {
            'sport': 'MLB',
            'team_name': 'Chicago Cubs',
            'stat_type': 'batting',
            'games': int(df['G'].sum()),
            'at_bats': int(df['AB'].sum()),
            'runs': int(df['R'].sum()),
            'hits': int(df['H'].sum()),
            'doubles': int(df['2B'].sum()),
            'triples': int(df['3B'].sum()),
            'home_runs': int(df['HR'].sum()),
            'rbi': int(df['RBI'].sum()),
            'walks': int(df['BB'].sum()),
            'strikeouts': int(df['SO'].sum()),
            'batting_avg': float(df['AVG'].mean()),
            'on_base_pct': float(df['OBP'].mean()),
            'slugging_pct': float(df['SLG'].mean()),
            'ops': float(df['OPS'].mean()),
            'source': 'ESPN',
            'stat_date': datetime.now().date()
        }

        insert_team_stats(stats)
        logger.info(f"Fetched ESPN team stats for {team_abbr}")
        return stats
    except Exception as e:
        logger.error(f"Error fetching ESPN team stats for {team_abbr}: {e}")
        return None

def fetch_teamrankings_player_stats(player_slug='kyle-tucker-4'):
    """
    Scrapes player batting stats from TeamRankings.
    """
    url = f"https://www.teamrankings.com/mlb/player/{player_slug}/stats/batting"
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # Extract season totals table
        table = soup.find('table', class_='tr-table')
        if not table:
            logger.warning(f"No batting stats table found for {player_slug}")
            return None

        row = table.find_all('tr')[1]  # First data row
        cols = row.find_all('td')
        stats = {
            'sport': 'MLB',
            'player_name': 'Kyle Tucker',
            'team_name': 'Chicago Cubs',
            'stat_type': 'batting',
            'games': int(cols[0].text),
            'at_bats': int(cols[2].text),
            'runs': int(cols[3].text),
            'hits': int(cols[4].text),
            'doubles': int(cols[6].text),
            'triples': int(cols[7].text),
            'home_runs': int(cols[8].text),
            'rbi': int(cols[9].text),
            'walks': int(cols[10].text),
            'strikeouts': int(cols[11].text),
            'stolen_bases': int(cols[12].text),
            'caught_stealing': int(cols[13].text),
            'batting_avg': float(cols[14].text),
            'on_base_pct': float(cols[15].text),
            'slugging_pct': float(cols[16].text),
            'ops': float(cols[17].text),
            'source': 'TeamRankings',
            'stat_date': datetime.now().date()
        }

        insert_player_stats(stats)
        logger.info(f"Fetched TeamRankings player stats for {player_slug}")
        return stats
    except Exception as e:
        logger.error(f"Error fetching TeamRankings player stats for {player_slug}: {e}")
        return None

def fetch_espn_player_splits(player_id='34967'):
    """
    Scrapes player batting splits from ESPN.
    """
    url = f"https://www.espn.com/mlb/player/splits/_/id/{player_id}/kyle-tucker"
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # Extract splits tables
        tables = soup.find_all('table', class_='Table')
        splits_data = []
        for table in tables:
            df = pd.read_html(str(table))[0]
            split_type = table.find_previous('h2').text.lower().replace(' ', '_')  # e.g., 'vs_left'
            for _, row in df.iterrows():
                split_value = row.get('Breakdown', row.get('Opponent', row.get('Stadium', row.get('Position', row.get('Count', row.get('Batting Order', row.get('Situation', 'Unknown')))))))
                stats = {
                    'sport': 'MLB',
                    'player_name': 'Kyle Tucker',
                    'team_name': 'Chicago Cubs',
                    'split_type': split_type,
                    'split_value': split_value,
                    'at_bats': int(row['AB']),
                    'runs': int(row['R']),
                    'hits': int(row['H']),
                    'doubles': int(row['2B']),
                    'triples': int(row['3B']),
                    'home_runs': int(row['HR']),
                    'rbi': int(row['RBI']),
                    'walks': int(row['BB']),
                    'strikeouts': int(row['SO']),
                    'stolen_bases': int(row['SB']),
                    'caught_stealing': int(row['CS']),
                    'batting_avg': float(row['AVG']),
                    'on_base_pct': float(row['OBP']),
                    'slugging_pct': float(row['SLG']),
                    'ops': float(row['OPS']),
                    'source': 'ESPN',
                    'stat_date': datetime.now().date()
                }
                splits_data.append(stats)
                insert_player_splits(stats)

        logger.info(f"Fetched ESPN player splits for player_id {player_id}")
        return splits_data
    except Exception as e:
        logger.error(f"Error fetching ESPN player splits for player_id {player_id}: {e}")
        return None

def fetch_mlb_stats_api():
    """
    Fetches team and player stats from MLB Stats API (free).
    """
    url = "https://statsapi.mlb.com/api/v1/teams/112/stats?season=2025&group=hitting"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        for team in data['stats'][0]['splits']:
            if team['team']['name'] == 'Chicago Cubs':
                stats = {
                    'sport': 'MLB',
                    'team_name': 'Chicago Cubs',
                    'stat_type': 'batting',
                    'games': int(team['stat']['gamesPlayed']),
                    'at_bats': int(team['stat']['atBats']),
                    'runs': int(team['stat']['runs']),
                    'hits': int(team['stat']['hits']),
                    'doubles': int(team['stat']['doubles']),
                    'triples': int(team['stat']['triples']),
                    'home_runs': int(team['stat']['homeRuns']),
                    'rbi': int(team['stat']['rbi']),
                    'walks': int(team['stat']['baseOnBalls']),
                    'strikeouts': int(team['stat']['strikeouts']),
                    'batting_avg': float(team['stat']['avg']),
                    'on_base_pct': float(team['stat']['obp']),
                    'slugging_pct': float(team['stat']['slg']),
                    'ops': float(team['stat']['ops']),
                    'source': 'MLB Stats API',
                    'stat_date': datetime.now().date()
                }
                insert_team_stats(stats)
                logger.info("Fetched MLB Stats API team stats for Chicago Cubs")
        return stats
    except Exception as e:
        logger.error(f"Error fetching MLB Stats API: {e}")
        return None

if __name__ == '__main__':
    # Fetch team stats
    fetch_teamrankings_team_stats('chicago-cubs')
    fetch_espn_team_stats('chc')
    fetch_mlb_stats_api()

    # Fetch player stats
    fetch_teamrankings_player_stats('kyle-tucker-4')
    fetch_espn_player_splits('34967')
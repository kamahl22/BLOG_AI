import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from supabase import create_client, Client
from dotenv import load_dotenv
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, filename='data_pipeline/pipeline.log', format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

# Validate environment variables
if not SUPABASE_URL or not SUPABASE_KEY:
    logger.error("SUPABASE_URL or SUPABASE_KEY not set in .env file")
    raise ValueError("Missing SUPABASE_URL or SUPABASE_KEY")

# Initialize Supabase client
try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    logger.info("Successfully connected to Supabase")
except Exception as e:
    logger.error(f"Failed to initialize Supabase client: {e}")
    raise

def execute_sql_file(file_path):
    """
    Executes a SQL file for migrations and tracks in migration_history.
    """
    try:
        migration_name = os.path.basename(file_path)
        result = supabase.table('migration_history').select('id').eq('migration_name', migration_name).execute()
        if result.data:
            logger.info(f"Migration {migration_name} already applied, skipping")
            return
        with open(file_path, 'r') as file:
            sql = file.read()
        supabase.rpc('execute_sql', {'query': sql}).execute()
        supabase.table('migration_history').insert({
            'migration_name': migration_name,
            'applied_at': datetime.utcnow().isoformat()
        }).execute()
        logger.info(f"Executed and tracked SQL file: {file_path}")
    except Exception as e:
        logger.error(f"Error executing SQL file {file_path}: {e}")
        raise

def insert_team_stats(data):
    try:
        supabase.table('team_stats').insert(data).execute()
        logger.info(f"Inserted team stats for {data['team_name']}")
        return {"success": True, "data": data}
    except Exception as e:
        logger.error(f"Error inserting team stats: {e}")
        return {"success": False, "error": str(e)}

def insert_odds_data(data):
    try:
        supabase.table('odds_data').insert(data).execute()
        logger.info(f"Inserted odds data: {data['home_team']} vs {data['away_team']}")
        return {"success": True, "data": data}
    except Exception as e:
        logger.error(f"Error inserting odds data: {e}")
        return {"success": False, "error": str(e)}

def insert_player_stats(data):
    try:
        supabase.table('player_stats').insert(data).execute()
        logger.info(f"Inserted player stats for {data['player_name']}")
        return {"success": True, "data": data}
    except Exception as e:
        logger.error(f"Error inserting player stats: {e}")
        return {"success": False, "error": str(e)}

def insert_player_splits(data):
    try:
        supabase.table('player_splits').insert(data).execute()
        logger.info(f"Inserted player splits for {data['player_name']} - {data['split_type']}")
        return {"success": True, "data": data}
    except Exception as e:
        logger.error(f"Error inserting player splits: {e}")
        return {"success": False, "error": str(e)}

def fetch_team_stats():
    try:
        data = supabase.table('team_stats').select('*').execute().data
        logger.info(f"Fetched {len(data)} team stats rows")
        return data
    except Exception as e:
        logger.error(f"Error fetching team stats: {e}")
        return []

def fetch_odds_data():
    try:
        data = supabase.table('odds_data').select('*').execute().data
        logger.info(f"Fetched {len(data)} odds data rows")
        return data
    except Exception as e:
        logger.error(f"Error fetching odds data: {e}")
        return []

def fetch_player_stats():
    try:
        data = supabase.table('player_stats').select('*').execute().data
        logger.info(f"Fetched {len(data)} player stats rows")
        return data
    except Exception as e:
        logger.error(f"Error fetching player stats: {e}")
        return []

def fetch_player_splits():
    try:
        data = supabase.table('player_splits').select('*').execute().data
        logger.info(f"Fetched {len(data)} player splits rows")
        return data
    except Exception as e:
        logger.error(f"Error fetching player splits: {e}")
        return []

# Sample data for testing, aligned with updated schemas
today = datetime.now().strftime('%Y-%m-%d')
current_season = 2025

team_stats_data = {
    'sport': 'MLB',
    'team_name': 'Testers',
    'stat_type': 'run_line_trends',
    'season': current_season,
    'games': 12,
    'at_bats': 400,
    'runs': 50,
    'hits': 100,
    'doubles': 20,
    'triples': 5,
    'home_runs': 15,
    'rbi': 45,
    'walks': 30,
    'strikeouts': 80,
    'batting_avg': 0.250,
    'on_base_pct': 0.320,
    'slugging_pct': 0.400,
    'ops': 0.720,
    'run_line_wins': 10,
    'run_line_losses': 2,
    'run_line_cover_pct': 0.833,
    'source': 'ManualTest',
    'stat_date': today
}

odds_data = {
    'sport': 'MLB',
    'home_team': 'Testers',
    'away_team': 'Mockers',
    'home_odds': -120,
    'away_odds': 110,
    'game_date': today
}

player_stats_data = {
    'sport': 'MLB',
    'player_name': 'Jane Doe',
    'team_name': 'Testers',
    'stat_type': 'batting',
    'season': current_season,
    'games': 25,
    'at_bats': 90,
    'runs': 15,
    'hits': 25,
    'doubles': 5,
    'triples': 1,
    'home_runs': 8,
    'rbi': 22,
    'walks': 10,
    'strikeouts': 20,
    'stolen_bases': 3,
    'caught_stealing': 1,
    'batting_avg': 0.278,
    'on_base_pct': 0.350,
    'slugging_pct': 0.450,
    'ops': 0.800,
    'source': 'ManualTest',
    'stat_date': today
}

player_splits_data = {
    'sport': 'MLB',
    'player_name': 'Jane Doe',
    'team_name': 'Testers',
    'split_type': 'vs_left',
    'split_value': 'vs. Left',
    'season': current_season,
    'at_bats': 30,
    'runs': 5,
    'hits': 9,
    'doubles': 2,
    'triples': 0,
    'home_runs': 3,
    'rbi': 9,
    'walks': 4,
    'strikeouts': 7,
    'stolen_bases': 1,
    'caught_stealing': 0,
    'batting_avg': 0.310,
    'on_base_pct': 0.380,
    'slugging_pct': 0.500,
    'ops': 0.880,
    'source': 'ManualTest',
    'stat_date': today
}

def print_summary(inserts, fetches):
    print('\n=== 📋 INSERTION RESULTS ===\n')
    for name, result in inserts.items():
        print(f"➡️ {name.replace('_', ' ').title()}: {'✅ Inserted' if result['success'] else '❌ Error'}")
        if result['success']:
            for k, v in result['data'].items():
                print(f'   - {k}: {v}')
        else:
            print(f'   ⚠️ Error: {result["error"]}')
        print()
    print('=== 📊 FETCHED DATA ===\n')
    for name, rows in fetches.items():
        print(f"🔍 {name.replace('_', ' ').title()} - {len(rows)} row(s):")
        for i, row in enumerate(rows, start=1):
            print(f'🧾 Row {i}:')
            for k, v in row.items():
                print(f'   - {k}: {v}')
            print()
        print('-' * 40)

if __name__ == '__main__':
    logger.info('Starting fetch_supabase.py test')
    try:
        insert_results = {
            'team_stats': insert_team_stats(team_stats_data),
            'odds_data': insert_odds_data(odds_data),
            'player_stats': insert_player_stats(player_stats_data),
            'player_splits': insert_player_splits(player_splits_data),
        }
        fetch_results = {
            'team_stats': fetch_team_stats(),
            'odds_data': fetch_odds_data(),
            'player_stats': fetch_player_stats(),
            'player_splits': fetch_player_splits(),
        }
        print_summary(insert_results, fetch_results)
        logger.info('Completed fetch_supabase.py test')
    except Exception as e:
        logger.error(f"Main execution failed: {e}")
        raise
import sys
import os
import requests
import logging
from dotenv import load_dotenv
from supabase import create_client, Client

# Add root path so imports work
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# Set up logging
logging.basicConfig(level=logging.INFO, filename='data_pipeline/pipeline.log')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Read Supabase credentials
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_ANON_KEY = os.getenv('SUPABASE_KEY')
SUPABASE_SERVICE_ROLE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY')  # New

# Initialize Supabase client for general use
supabase: Client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

def execute_sql_file(file_path):
    """
    Executes a SQL file against Supabase using the REST API.
    Requires Service Role Key for permission.
    """
    try:
        with open(file_path, 'r') as file:
            sql_content = file.read()

        headers = {
            "apikey": SUPABASE_SERVICE_ROLE_KEY,
            "Authorization": f"Bearer {SUPABASE_SERVICE_ROLE_KEY}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

        payload = {
            "sql": sql_content
        }

        response = requests.post(
            f"{SUPABASE_URL}/rest/v1/rpc/execute_sql",
            headers=headers,
            json=payload
        )

        if response.status_code != 200:
            logger.error(f"Failed to execute {file_path}: {response.text}")
            response.raise_for_status()

        logger.info(f"Successfully executed SQL file: {file_path}")
        print(f"✅ Successfully executed: {file_path}")

    except Exception as e:
        logger.error(f"Error executing SQL file {file_path}: {e}")
        raise

def insert_odds_data(data):
    """
    Inserts odds data into the odds_data table.
    """
    try:
        supabase.table('odds_data').insert(data).execute()
        logger.info(f"Inserted odds data: {data['home_team']} vs {data['away_team']}")
    except Exception as e:
        logger.error(f"Error inserting odds data: {e}")

def insert_team_stats(data):
    """
    Inserts team stats into the team_stats table.
    """
    try:
        supabase.table('team_stats').insert(data).execute()
        logger.info(f"Inserted team stats for {data['team_name']}")
    except Exception as e:
        logger.error(f"Error inserting team stats: {e}")

def insert_player_stats(data):
    """
    Inserts player stats into the player_stats table.
    """
    try:
        supabase.table('player_stats').insert(data).execute()
        logger.info(f"Inserted player stats for {data['player_name']}")
    except Exception as e:
        logger.error(f"Error inserting player stats: {e}")

def insert_player_splits(data):
    """
    Inserts player splits into the player_splits table.
    """
    try:
        supabase.table('player_splits').insert(data).execute()
        logger.info(f"Inserted player splits for {data['player_name']} - {data['split_type']}: {data['split_value']}")
    except Exception as e:
        logger.error(f"Error inserting player splits: {e}")
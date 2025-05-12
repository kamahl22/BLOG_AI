import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from supabase import create_client
from dotenv import load_dotenv
import requests
import logging
import importlib.util

# Configure logging
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

def check_environment():
    """Check environment setup."""
    logger.info("Checking environment...")
    try:
        if os.path.exists('.env'):
            load_dotenv()
            supabase_url = os.getenv('SUPABASE_URL')
            supabase_key = os.getenv('SUPABASE_KEY')
            odds_api_key = os.getenv('ODDS_API_KEY')
            logger.info(f"SUPABASE_URL: {'Set' if supabase_url else 'Not set'}")
            logger.info(f"SUPABASE_KEY: {'Set' if supabase_key else 'Not set'}")
            logger.info(f"ODDS_API_KEY: {'Set' if odds_api_key else 'Not set'}")
        else:
            logger.error(".env file not found")
        logger.info("Environment check complete")
    except Exception as e:
        logger.error(f"Environment check failed: {e}")

def check_supabase():
    """Check Supabase connection and tables."""
    logger.info("Checking Supabase connection...")
    try:
        load_dotenv()
        supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_KEY'))
        # Test connection
        tables = ['team_stats', 'odds_data', 'player_stats', 'player_splits']
        for table in tables:
            response = supabase.table(table).select('id').limit(1).execute()
            logger.info(f"Table {table}: Accessible")
        logger.info("Supabase check complete")
    except Exception as e:
        logger.error(f"Supabase check failed: {e}")

def check_http_requests():
    """Check HTTP requests to data sources."""
    logger.info("Checking HTTP requests...")
    try:
        # TeamRankings
        response = requests.get('https://www.teamrankings.com/mlb/team/chicago-cubs/stats', headers={'User-Agent': 'Mozilla/5.0'})
        logger.info(f"TeamRankings status: {response.status_code}")
        # The Odds API
        odds_url = f"https://api.the-odds-api.com/v4/sports/baseball_mlb/odds/?apiKey={os.getenv('ODDS_API_KEY')}&regions=us&markets=h2h"
        response = requests.get(odds_url)
        logger.info(f"The Odds API status: {response.status_code}")
        # ESPN
        response = requests.get('https://www.espn.com/mlb/player/stats/_/id/33192', headers={'User-Agent': 'Mozilla/5.0'})
        logger.info(f"ESPN stats status: {response.status_code}")
        logger.info("HTTP requests check complete")
    except Exception as e:
        logger.error(f"HTTP requests check failed: {e}")

def check_dependencies():
    """Check required dependencies."""
    logger.info("Checking dependencies...")
    try:
        for module in ['supabase', 'requests', 'beautifulsoup4', 'dotenv']:
            spec = importlib.util.find_spec(module)
            logger.info(f"{module}: {'Installed' if spec else 'Not installed'}")
        logger.info("Dependencies check complete")
    except Exception as e:
        logger.error(f"Dependencies check failed: {e}")

def check_fetch_supabase():
    """Check fetch_supabase.py import."""
    logger.info("Checking fetch_supabase.py...")
    try:
        from fetch_supabase import insert_team_stats
        logger.info("fetch_supabase.py imported successfully")
    except ImportError as e:
        logger.error(f"Failed to import fetch_supabase.py: {e}")

if __name__ == "__main__":
    logger.info("Starting diagnostic checks")
    check_environment()
    check_dependencies()
    check_fetch_supabase()
    check_supabase()
    check_http_requests()
    logger.info("Diagnostic checks complete")
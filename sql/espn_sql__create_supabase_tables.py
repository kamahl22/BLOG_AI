import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from supabase import create_client
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    filename='sql/logs/migration.log',
    format='%(asctime)s - %(levelname)s - %(message)s',
    filemode='a'
)
logger = logging.getLogger(__name__)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
console_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logger.addHandler(console_handler)

# SQL scripts for table creation
TABLE_SCHEMAS = {
    'migration_history': """
        CREATE TABLE migration_history (
            id SERIAL PRIMARY KEY,
            migration_name VARCHAR(100) NOT NULL,
            applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """,
    'team_stats': """
        CREATE TABLE team_stats (
            id SERIAL PRIMARY KEY,
            sport VARCHAR(50) NOT NULL,
            team_name VARCHAR(100) NOT NULL,
            stat_type VARCHAR(50) NOT NULL,
            season INTEGER NOT NULL,
            games INTEGER,
            at_bats INTEGER,
            runs INTEGER,
            hits INTEGER,
            doubles INTEGER,
            triples INTEGER,
            home_runs INTEGER,
            rbi INTEGER,
            walks INTEGER,
            strikeouts INTEGER,
            batting_avg FLOAT,
            on_base_pct FLOAT,
            slugging_pct FLOAT,
            ops FLOAT,
            run_line_wins INTEGER,
            run_line_losses INTEGER,
            run_line_cover_pct FLOAT,
            source VARCHAR(100),
            stat_date DATE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """,
    'player_stats': """
        CREATE TABLE player_stats (
            id SERIAL PRIMARY KEY,
            sport VARCHAR(50) NOT NULL,
            player_name VARCHAR(100) NOT NULL,
            team_name VARCHAR(100) NOT NULL,
            stat_type VARCHAR(50) NOT NULL,
            season INTEGER NOT NULL,
            games INTEGER,
            at_bats INTEGER,
            runs INTEGER,
            hits INTEGER,
            doubles INTEGER,
            triples INTEGER,
            home_runs INTEGER,
            rbi INTEGER,
            walks INTEGER,
            strikeouts INTEGER,
            stolen_bases INTEGER,
            caught_stealing INTEGER,
            batting_avg FLOAT,
            on_base_pct FLOAT,
            slugging_pct FLOAT,
            ops FLOAT,
            source VARCHAR(100),
            stat_date DATE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """,
    'player_splits': """
        CREATE TABLE player_splits (
            id SERIAL PRIMARY KEY,
            sport VARCHAR(50) NOT NULL,
            player_name VARCHAR(100) NOT NULL,
            team_name VARCHAR(100) NOT NULL,
            split_type VARCHAR(50) NOT NULL,
            split_value VARCHAR(100) NOT NULL,
            season INTEGER NOT NULL,
            at_bats INTEGER,
            runs INTEGER,
            hits INTEGER,
            doubles INTEGER,
            triples INTEGER,
            home_runs INTEGER,
            rbi INTEGER,
            walks INTEGER,
            strikeouts INTEGER,
            stolen_bases INTEGER,
            caught_stealing INTEGER,
            batting_avg FLOAT,
            on_base_pct FLOAT,
            slugging_pct FLOAT,
            ops FLOAT,
            source VARCHAR(100),
            stat_date DATE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """,
    'odds_data': """
        CREATE TABLE odds_data (
            id SERIAL PRIMARY KEY,
            sport VARCHAR(50) NOT NULL,
            home_team VARCHAR(100) NOT NULL,
            away_team VARCHAR(100) NOT NULL,
            home_odds INTEGER,
            away_odds INTEGER,
            game_date DATE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """
}

def execute_sql(supabase, sql, description):
    """Execute SQL command using Supabase RPC."""
    try:
        logger.debug(f"Executing SQL for {description}:\n{sql}")
        result = supabase.rpc('execute_sql', {'query': sql}).execute()
        logger.info(f"Successfully executed {description}")
        return result
    except Exception as e:
        logger.error(f"Failed to execute {description}: {str(e)}")
        raise

def drop_all_tables(supabase):
    """Drop all project tables."""
    logger.info("Dropping all tables")
    drop_sql = """
    DROP TABLE IF EXISTS team_stats CASCADE;
    DROP TABLE IF EXISTS player_stats CASCADE;
    DROP TABLE IF EXISTS player_splits CASCADE;
    DROP TABLE IF EXISTS odds_data CASCADE;
    DROP TABLE IF EXISTS migration_history CASCADE;
    """
    execute_sql(supabase, drop_sql, "drop all tables")

def verify_schema(supabase):
    """Verify table schemas."""
    logger.info("Verifying table schemas")
    tables = {
        'team_stats': ['season', 'games', 'batting_avg'],
        'player_stats': ['season', 'games', 'batting_avg'],
        'player_splits': ['season', 'split_type', 'batting_avg'],
        'odds_data': ['home_odds', 'away_odds'],
        'migration_history': ['migration_name']
    }
    for table, columns in tables.items():
        try:
            schema = supabase.table(table).select(','.join(columns)).limit(1).execute()
            logger.info(f"Table {table}: Schema verified")
        except Exception as e:
            logger.error(f"Table {table}: Schema verification failed: {str(e)}")
            raise

def create_tables():
    """Create all Supabase tables."""
    logger.info("Starting table creation")
    load_dotenv()
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_KEY')
    if not supabase_url or not supabase_key:
        logger.error("SUPABASE_URL or SUPABASE_KEY not set")
        sys.exit(1)

    supabase = create_client(supabase_url, supabase_key)

    # Drop existing tables
    drop_all_tables(supabase)

    # Create tables
    for table_name, sql in TABLE_SCHEMAS.items():
        execute_sql(supabase, sql, f"create {table_name} table")

    # Verify schemas
    verify_schema(supabase)

    # Log migration history
    for table_name in TABLE_SCHEMAS.keys():
        try:
            supabase.table('migration_history').insert({
                'migration_name': f'create_{table_name}',
                'applied_at': 'now()'
            }).execute()
            logger.info(f"Logged migration for {table_name}")
        except Exception as e:
            logger.error(f"Failed to log migration for {table_name}: {str(e)}")
            raise

    logger.info("All tables created successfully")

if __name__ == "__main__":
    try:
        create_tables()
    except Exception as e:
        logger.error(f"Table creation failed: {str(e)}")
        sys.exit(1)
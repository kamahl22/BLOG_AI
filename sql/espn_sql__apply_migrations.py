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

def execute_sql_file(file_path, supabase):
    """Execute SQL file using Supabase RPC."""
    try:
        with open(file_path, 'r') as f:
            sql = f.read()
        logger.debug(f"Executing SQL from {file_path}:\n{sql}")
        result = supabase.rpc('execute_sql', {'query': sql}).execute()
        logger.info(f"Successfully executed {file_path}")
        return result
    except Exception as e:
        logger.error(f"Failed to execute {file_path}: {str(e)}")
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
    try:
        supabase.rpc('execute_sql', {'query': drop_sql}).execute()
        logger.info("All tables dropped successfully")
    except Exception as e:
        logger.error(f"Failed to drop tables: {str(e)}")
        raise

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

def check_existing_tables(supabase):
    """Check for existing tables."""
    logger.info("Checking existing tables")
    try:
        result = supabase.rpc('execute_sql', {
            'query': """
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
            AND table_name IN ('team_stats', 'player_stats', 'player_splits', 'odds_data', 'migration_history')
            """
        }).execute()
        tables = [row['table_name'] for row in result.data]
        logger.info(f"Existing tables: {tables}")
        return tables
    except Exception as e:
        logger.error(f"Failed to check existing tables: {str(e)}")
        return []

def apply_migrations():
    """Apply all migrations from SQL files."""
    logger.info("Starting migration application")
    load_dotenv()
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
    if not supabase_url or not supabase_key:
        logger.error("SUPABASE_URL or SUPABASE_KEY not set")
        sys.exit(1)

    supabase = create_client(supabase_url, supabase_key)
    
    # Check existing tables
    existing_tables = check_existing_tables(supabase)
    logger.info(f"Found existing tables: {existing_tables}")

    # Drop existing tables
    drop_all_tables(supabase)

    # Apply migrations
    migration_files = [
        'sql/migrations/002_create_migration_history_table.sql',
        'sql/migrations/003_create_team_stats_table.sql',
        'sql/migrations/004_create_player_stats_table.sql',
        'sql/migrations/005_create_player_splits_table.sql',
        'sql/migrations/006_fix_odds_data_table.sql'
    ]
    
    for file in migration_files:
        if not os.path.exists(file):
            logger.error(f"Migration file not found: {file}")
            sys.exit(1)
        execute_sql_file(file, supabase)
    
    # Verify schemas
    verify_schema(supabase)

    # Log migration history
    for file in migration_files:
        migration_name = os.path.basename(file)
        try:
            supabase.table('migration_history').insert({
                'migration_name': migration_name,
                'applied_at': 'now()'
            }).execute()
            logger.info(f"Logged migration: {migration_name}")
        except Exception as e:
            logger.error(f"Failed to log migration {migration_name}: {str(e)}")
            raise

    logger.info("All migrations applied successfully")

if __name__ == "__main__":
    try:
        apply_migrations()
    except Exception as e:
        logger.error(f"Migration application failed: {str(e)}")
        sys.exit(1)
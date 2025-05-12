import os
import shutil
import logging
from pathlib import Path

# Set up logging
os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    filename="logs/update_tree.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger()

def create_directories(dirs):
    """Create directories if they don't exist."""
    for d in dirs:
        os.makedirs(d, exist_ok=True)
        logger.info(f"Created directory: {d}")

def create_files(files):
    """Create empty files if they don't exist."""
    for f in files:
        Path(f).parent.mkdir(parents=True, exist_ok=True)
        Path(f).touch()
        logger.info(f"Created file: {f}")

def move_files(moves):
    """Move files from source to destination."""
    for src, dst in moves:
        if os.path.exists(src):
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.move(src, dst)
            logger.info(f"Moved {src} to {dst}")
        else:
            logger.warning(f"Source not found: {src}")

def delete_paths(paths):
    """Delete files or directories."""
    for p in paths:
        if os.path.isfile(p):
            os.remove(p)
            logger.info(f"Deleted file: {p}")
        elif os.path.isdir(p):
            shutil.rmtree(p, ignore_errors=True)
            logger.info(f"Deleted directory: {p}")
        else:
            logger.warning(f"Path not found: {p}")

def main():
    # Directories to create
    new_dirs = [
        "data_pipeline/storage/raw/mlb",
        "data_pipeline/storage/raw/other_sports",
        "database/migrations",
        "database/queries",
        "logs"
    ]
    create_directories(new_dirs)

    # Files to create
    new_files = [
        "data_pipeline/fetch/fetch_all_data.py",
        "database/backup_supabase.py",
        "database/insert_data.py",
        ".env",
        "logs/errors.log"
    ]
    create_files(new_files)

    # Files to move
    moves = [
        ("sql/migrations/000_create_migration_history_table.sql", "database/migrations/000_create_migration_history_table.sql"),
        ("sql/migrations/001_create_odds_table.sql", "database/migrations/001_create_odds_table.sql"),
        ("sql/migrations/002_fix_odds_moneyline.sql", "database/migrations/002_fix_odds_moneyline.sql"),
        ("sql/migrations/003_create_team_stats_table.sql", "database/migrations/003_create_team_stats_table.sql"),
        ("sql/migrations/004_create_player_stats_table.sql", "database/migrations/004_create_player_stats_table.sql"),
        ("sql/migrations/005_create_player_splits_table.sql", "database/migrations/005_create_player_splits_table.sql"),
        ("sql/migrations/006_fix_odds_data_table.sql", "database/migrations/006_fix_odds_data_table.sql"),
        ("sql/migrations/apply_migrations.py", "database/migrations/apply_migrations.py"),
        ("sql/queries/check_odds_data.sql", "database/queries/check_odds_data.sql"),
        ("sql/queries/check_odds_schema.sql", "database/queries/check_odds_schema.sql"),
        ("data_pipeline/merge_data.py", "data_pipeline/preprocess/merge_data.py"),
        ("data_pipeline/fetch_teamrankings.py", "data_pipeline/fetch/fetch_team_rankings.py"),
        ("run_migrations.py", "database/migrations/apply_migrations.py"),  # Overwrite if exists
        ("test_db_connection.py", "tests/test_db.py")
    ]
    move_files(moves)

    # Files and directories to delete
    deletes = [
        "data_pipeline/fetch_news.py",
        "data_pipeline/fetch_odds.py",
        "data_pipeline/fetch_supabase.py",
        "data_pipeline/info",
        "data_pipeline/scripts",
        "data_pipeline/.DS_Store",
        "bot.py",
        "cogs",
        "config.py",
        "Blockchain_structure",
        "Discord_Bot_Structure",
        "directory_structure.txt",
        "structure_scripts",
        "venv"
    ]
    delete_paths(deletes)

    logger.info("Directory structure update complete.")

if __name__ == "__main__":
    main()
import os
import sys
import psycopg2
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

DB_HOST = os.getenv("SUPABASE_DB_HOST")
DB_PORT = os.getenv("SUPABASE_DB_PORT")
DB_NAME = os.getenv("SUPABASE_DB_NAME")
DB_USER = os.getenv("SUPABASE_DB_USER")
DB_PASSWORD = os.getenv("SUPABASE_DB_PASSWORD")

MIGRATIONS_FOLDER = os.path.join(os.getcwd(), "sql", "migrations")

def connect_to_db():
    connection = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        sslmode="require"
    )
    connection.autocommit = True
    return connection

def ensure_migration_history_table(cursor):
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS public.migration_history (
        id SERIAL PRIMARY KEY,
        filename VARCHAR(255) UNIQUE NOT NULL,
        applied_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
    );
    """
    cursor.execute(create_table_sql)

def get_applied_migrations(cursor):
    cursor.execute("SELECT filename FROM public.migration_history;")
    result = cursor.fetchall()
    applied = {row[0] for row in result}
    return applied

def save_migration_record(cursor, filename):
    cursor.execute(
        "INSERT INTO public.migration_history (filename) VALUES (%s);",
        (filename,)
    )

def run_migrations():
    try:
        connection = connect_to_db()
        cursor = connection.cursor()

        ensure_migration_history_table(cursor)

        migration_files = sorted([
            f for f in os.listdir(MIGRATIONS_FOLDER) if f.endswith(".sql")
        ])

        if not migration_files:
            print("⚠️ No SQL migration files found.")
            return

        print(f"Found {len(migration_files)} migration files.")

        applied_migrations = get_applied_migrations(cursor)

        for filename in migration_files:
            if filename in applied_migrations:
                print(f"⏭️ Skipping already applied migration: {filename}")
                continue

            file_path = os.path.join(MIGRATIONS_FOLDER, filename)
            print(f"🚀 Running migration: {filename}")

            with open(file_path, 'r') as sql_file:
                sql = sql_file.read()

            try:
                cursor.execute(sql)
                save_migration_record(cursor, filename)
                print(f"✅ Successfully ran: {filename}")
            except Exception as e:
                print(f"❌ Failed to run migration {filename}: {e}")
                cursor.close()
                connection.close()
                sys.exit(1)

        cursor.close()
        connection.close()
        print("✅ All migrations completed successfully.")

    except Exception as e:
        print(f"❌ Error connecting to database: {e}")
        sys.exit(1)

if __name__ == "__main__":
    run_migrations()
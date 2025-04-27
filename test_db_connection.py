import os
import psycopg2
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

DB_HOST = os.getenv("SUPABASE_DB_HOST")
DB_PORT = os.getenv("SUPABASE_DB_PORT")
DB_NAME = os.getenv("SUPABASE_DB_NAME")
DB_USER = os.getenv("SUPABASE_DB_USER")
DB_PASSWORD = os.getenv("SUPABASE_DB_PASSWORD")

def test_connection():
    try:
        connection = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            sslmode="require"
        )
        cursor = connection.cursor()
        cursor.execute("SELECT version();")
        db_version = cursor.fetchone()
        print(f"✅ Connected to database! PostgreSQL version: {db_version[0]}")

        cursor.close()
        connection.close()

    except Exception as e:
        print(f"❌ Failed to connect to database: {e}")

if __name__ == "__main__":
    test_connection()
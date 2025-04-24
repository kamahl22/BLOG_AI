import os
from dotenv import load_dotenv

# This loads variables like ODDS_API_KEY, etc., from your .env file
load_dotenv()

ODDS_API_KEY = os.getenv("ODDS_API_KEY")
NEWS_API_KEY = os.getenv("NEWS_API_KEY")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
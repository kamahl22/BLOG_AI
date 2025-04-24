#!/bin/bash

# Define base path
BASE_PATH="../data_pipeline"

# Make sure the directory exists
mkdir -p "$BASE_PATH"

# Create each Python file with initial content
declare -A FILES=(
  ["fetch_odds.py"]="import requests

def fetch_odds():
    url = \"https://api.the-odds-api.com/v4/sports/upcoming/odds\"
    params = {
        'apiKey': 'YOUR_ODDS_API_KEY',
        'regions': 'us',
        'markets': 'h2h,spreads',
        'oddsFormat': 'decimal'
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f\"Failed to fetch odds: {response.status_code}\")"
  
  ["fetch_news.py"]="import requests

def fetch_news():
    url = \"https://newsapi.org/v2/everything\"
    params = {
        'q': 'sports',
        'apiKey': 'YOUR_NEWS_API_KEY',
        'language': 'en',
        'sortBy': 'relevancy',
        'pageSize': 5
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()[\"articles\"]
    else:
        raise Exception(f\"Failed to fetch news: {response.status_code}\")"

  ["fetch_supabase.py"]="from supabase import create_client, Client
import os

def fetch_supabase_data():
    url = os.getenv(\"SUPABASE_URL\")
    key = os.getenv(\"SUPABASE_KEY\")
    supabase: Client = create_client(url, key)
    data = supabase.table(\"historical_matches\").select(\"*\").execute()
    return data.data"

  ["merge_data.py"]="def merge_data(odds_data, news_data, supabase_data):
    return {
        \"odds\": odds_data,
        \"news\": news_data,
        \"historical\": supabase_data
    }"

  ["summarize.py"]="import openai
import os

def summarize_data(merged_data):
    openai.api_key = os.getenv(\"OPENAI_API_KEY\")
    prompt = f\"Summarize this betting data for a Discord user: {merged_data}\"
    response = openai.ChatCompletion.create(
        model=\"gpt-4\",
        messages=[{\"role\": \"user\", \"content\": prompt}]
    )
    return response['choices'][0]['message']['content']"

  ["config.py"]="import os
from dotenv import load_dotenv

load_dotenv()

ODDS_API_KEY = os.getenv(\"ODDS_API_KEY\")
NEWS_API_KEY = os.getenv(\"NEWS_API_KEY\")
SUPABASE_URL = os.getenv(\"SUPABASE_URL\")
SUPABASE_KEY = os.getenv(\"SUPABASE_KEY\")
OPENAI_API_KEY = os.getenv(\"OPENAI_API_KEY\")"
)

# Write each file
for file in "${!FILES[@]}"; do
  echo "${FILES[$file]}" > "$BASE_PATH/$file"
done

echo "✅ Pipeline files created in $BASE_PATH"
import requests
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("ODDS_API_KEY")
url = f"https://api.the-odds-api.com/v4/sports/baseball_mlb/odds/?apiKey={api_key}&regions=us&markets=h2h,spreads,totals"
response = requests.get(url)
print(f"Status: {response.status_code}")
print(f"Response: {response.text}")
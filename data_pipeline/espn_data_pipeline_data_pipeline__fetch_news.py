# BLOG_AI/data_pipeline/fetch_news.py
import requests
import os
from dotenv import load_dotenv

load_dotenv()

def fetch_news():
    url = "https://newsapi.org/v2/everything"
    params = {
        'q': 'sports',
        'apiKey': os.getenv("NEWS_API_KEY"),
        'language': 'en',
        'sortBy': 'relevancy',
        'pageSize': 5
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()["articles"]
    else:
        raise Exception(f"Failed to fetch news: {response.status_code}")
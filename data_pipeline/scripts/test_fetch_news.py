import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from data_pipeline.fetch_news import fetch_news

try:
    articles = fetch_news()
    print("✅ Successfully fetched news articles:")
    for i, article in enumerate(articles, 1):
        print(f"{i}. {article['title']}")
except Exception as e:
    print(f"❌ Error fetching news: {e}")
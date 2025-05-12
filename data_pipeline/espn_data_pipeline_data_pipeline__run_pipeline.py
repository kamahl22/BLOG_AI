from fetch_odds import fetch_odds
from fetch_news import fetch_news
from fetch_supabase import fetch_supabase_data
from merge_data import merge_data
from summarize import summarize_data

def main():
    print("🔄 Fetching betting odds...")
    odds_data = fetch_odds()

    print("📰 Fetching sports news...")
    news_data = fetch_news()

    print("📊 Fetching historical data from Supabase...")
    supabase_data = fetch_supabase_data()

    print("🔗 Merging data...")
    merged_data = merge_data(odds_data, news_data, supabase_data)

    print("🧠 Summarizing data with OpenAI...")
    summary = summarize_data(merged_data)

    print("✅ Summary ready:")
    print(summary)

if __name__ == "__main__":
    main()
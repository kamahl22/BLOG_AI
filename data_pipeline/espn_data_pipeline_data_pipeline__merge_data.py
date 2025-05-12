def merge_data(odds_data, news_data, supabase_data):
    # This is a very simple merge, placing the data into a dictionary.
    return {
        "odds": odds_data,
        "news": news_data,
        "historical": supabase_data
    }
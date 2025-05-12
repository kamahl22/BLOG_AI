from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time
from tabulate import tabulate
# import supabase
# from dotenv import load_dotenv
# import os

# load_dotenv()
# client = supabase.create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

def scrape_blue_jays_news():
    print("📡 Fetching Toronto Blue Jays news...")
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    driver = webdriver.Chrome(options=chrome_options)
    try:
        driver.get("https://www.espn.com/mlb/team/_/name/tor/toronto-blue-jays")
        time.sleep(3)
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, "html.parser")
        news_items = soup.find_all("article", class_="headlineStack__list")
        all_data = []
        for item in news_items[:5]:  # Limit to 5 news items
            headline = item.find("a")
            if headline:
                title = headline.text.strip()
                link = headline["href"]
                all_data.append([title, link])
        if all_data:
            print("Toronto Blue Jays News:")
            print(tabulate(all_data, headers=["Headline", "Link"], tablefmt="grid"))
            # client.table("team_news").insert([{"team": "toronto-blue-jays", "headline": row[0], "link": row[1]} for row in all_data]).execute()
        return all_data
    except Exception as e:
        print(f"Error scraping news: {str(e)}")
        return []
    finally:
        driver.quit()

if __name__ == "__main__":
    news = scrape_blue_jays_news()
    print(f"✅ Scraped {len(news)} news items." if news else "❌ No news data.")
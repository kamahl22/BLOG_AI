import sys
import os

# Add project root (BLOG_AI/) to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from data_pipeline.fetch_odds import fetch_odds

try:
    odds_data = fetch_odds()
    print("✅ Successfully fetched odds:")
    print(odds_data[:1])  # Show just one sample
except Exception as e:
    print("❌ Error fetching odds:", e)
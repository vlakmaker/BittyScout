# test_adzuna_scraper.py
import os
import sys
import yaml
from dotenv import load_dotenv

# --- Project Setup ---
load_dotenv()
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
# --- End Setup ---

from utils.db_utils import create_jobs_table_if_not_exist, get_db_connection
from agents.scraper.sources.adzuna_scraper import AdzunaScraper

def load_config(config_path="config/job_sources.yml"):
    full_path = os.path.join(PROJECT_ROOT, config_path)
    try:
        with open(full_path, 'r') as f: return yaml.safe_load(f)
    except Exception: return {}

if __name__ == "__main__":
    if not os.getenv("ADZUNA_APP_ID") or not os.getenv("ADZUNA_APP_KEY"):
        print("🚨 CRITICAL: ADZUNA_APP_ID or ADZUNA_APP_KEY is not set in your .env file.")
        print("   Please sign up at https://developer.adzuna.com/ and add your credentials.")
        sys.exit(1)
        
    create_jobs_table_if_not_exist()

    config = load_config()
    test_configs = config.get("Adzuna", [])

    if not test_configs:
        print("⚠️ No Adzuna search configurations found in 'config/job_sources.yml'.")
        sys.exit(1)

    print(f"🧪 Testing Adzuna scraper...")
    scraper = AdzunaScraper(search_configs=test_configs)
    processed, new = scraper.fetch_jobs()
    print(f"\n🔍 Processed {processed} job offers. Newly inserted: {new}.\n")

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT title, company_name, location
        FROM jobs WHERE platform_source='Adzuna' ORDER BY date_fetched DESC LIMIT 5
    """)
    results = cursor.fetchall()
    if results:
        print("--- Sample of jobs inserted/updated in DB ---")
        for row in results: print(f"📄 {row['company_name']} ({row['location']}): {row['title'][:50]}...")
    else:
        print("❓ No Adzuna jobs found in the database after the run.")
    conn.close()

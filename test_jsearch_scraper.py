# test_jsearch_scraper.py
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
from agents.scraper.sources.jsearch_scraper import JsearchScraper

def load_config(config_path="config/job_sources.yml"):
    full_path = os.path.join(PROJECT_ROOT, config_path)
    try:
        with open(full_path, 'r') as f: return yaml.safe_load(f)
    except Exception: return {}

if __name__ == "__main__":
    if not os.getenv("JSEARCH_API_KEY"):
        print("🚨 CRITICAL: JSEARCH_API_KEY is not set in your .env file.")
        print("   Please sign up at https://rapidapi.com/letscrape-6bRBa3QguO5/api/jsearch and add your key.")
        sys.exit(1)
        
    create_jobs_table_if_not_exist()

    config = load_config()
    test_queries = config.get("JSearch", [])

    if not test_queries:
        print("⚠️ No JSearch queries found in 'config/job_sources.yml' under the 'JSearch' key.")
        sys.exit(1)

    print(f"🧪 Testing JSearch scraper with queries: {test_queries}")
    scraper = JsearchScraper(search_queries=test_queries)
    processed, new = scraper.fetch_jobs()
    print(f"\n🔍 Processed {processed} job offers. Newly inserted: {new}.\n")

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT title, company_name, job_url
        FROM jobs WHERE platform_source='JSearch' ORDER BY date_fetched DESC LIMIT 5
    """)
    results = cursor.fetchall()
    if results:
        print("--- Sample of jobs inserted/updated in DB ---")
        for row in results: print(f"📄 {row['company_name']}: {row['title'][:50]}...")
    else:
        print("❓ No JSearch jobs found in the database after the run.")
    conn.close()

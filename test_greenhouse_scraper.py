# test_greenhouse_scraper.py
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
from agents.scraper.sources.greenhouse_scraper import GreenhouseScraper

def load_config(config_path="config/job_sources.yml"):
    """Loads the YAML configuration file."""
    full_path = os.path.join(PROJECT_ROOT, config_path)
    try:
        with open(full_path, 'r') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        print(f"❌ Error: Configuration file not found at {full_path}")
        return {}
    except yaml.YAMLError as e:
        print(f"❌ Error parsing YAML file: {e}")
        return {}

if __name__ == "__main__":
    create_jobs_table_if_not_exist()

    config = load_config()
    test_companies = config.get("Greenhouse", [])

    if not test_companies:
        print("⚠️ No Greenhouse companies found in 'config/job_sources.yml' under the 'Greenhouse' key.")
        sys.exit(1)

    print(f"🧪 Testing Greenhouse scraper with companies: {test_companies}")
    scraper = GreenhouseScraper(company_identifiers=test_companies)
    processed, new = scraper.fetch_jobs()
    print(f"\n🔍 Processed {processed} job offers. Newly inserted: {new}.\n")

    # Show some entries from the database to confirm
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT title, company_name, job_url, LENGTH(full_description_text) as text_len, last_seen_on_platform
        FROM jobs
        WHERE platform_source='Greenhouse'
        ORDER BY date_fetched DESC
        LIMIT 5
    """)
    
    results = cursor.fetchall()
    if results:
        print("--- Sample of jobs inserted/updated in DB ---")
        for row in results:
            print(f"📄 {row['company_name']}: {row['title'][:40]}... — Desc Len: {row['text_len']} — Last Seen: {row['last_seen_on_platform']}")
    else:
        print("❓ No Greenhouse jobs found in the database after the run.")
        
    conn.close()

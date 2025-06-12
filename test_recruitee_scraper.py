# test_recruitee_scraper.py
import os
import sys
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Set working dir
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
os.chdir(PROJECT_ROOT)

# Fix import path for utils
if "utils" not in sys.path:
    sys.path.insert(0, os.path.join(PROJECT_ROOT, "utils"))

# --- Imports ---
from utils.db_utils import create_jobs_table_if_not_exist, get_db_connection
from agents.scraper.sources.recruitee_scraper import RecruiteeScraper
from utils.source_config_loader import load_job_sources

# --- Main ---
if __name__ == "__main__":
    create_jobs_table_if_not_exist()

    config = load_job_sources("config/job_sources.yml")
    test_companies = config.get("recruitee_companies", [])

    if not test_companies:
        print("⚠️ No Recruitee companies configured in config/source.yml.")
        sys.exit(1)

    scraper = RecruiteeScraper(company_identifiers=test_companies)
    processed, new = scraper.fetch_jobs()
    print(f"\n🔍 Processed {processed} job offers. Newly inserted: {new}.\n")

    # Show DB entries
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT title, job_url, LENGTH(full_description_text) as text_len, last_seen_on_platform
        FROM jobs
        WHERE platform_source='Recruitee'
        ORDER BY date_fetched DESC
        LIMIT 5
    """)
    for row in cursor.fetchall():
        print(f"📄 {row['title'][:40]} — Desc Len: {row['text_len']} — Last Seen: {row['last_seen_on_platform']}")
    conn.close()

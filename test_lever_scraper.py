import os
from dotenv import load_dotenv
from utils.db_utils import create_jobs_table_if_not_exist, get_db_connection
from utils.source_config_loader import load_job_sources
from agents.scraper.sources.lever_scraper import LeverScraper

load_dotenv()
create_jobs_table_if_not_exist()

config = load_job_sources()
test_companies = config.get("lever_companies", [])

scraper = LeverScraper(company_identifiers=test_companies)
processed, new = scraper.fetch_jobs()

print(f"\n🔍 Processed {processed} job offers. Newly inserted: {new}.\n")

conn = get_db_connection()
cursor = conn.cursor()
cursor.execute("""
    SELECT title, job_url, LENGTH(full_description_text) as text_len, last_seen_on_platform
    FROM jobs
    WHERE platform_source='Lever'
    ORDER BY date_fetched DESC
    LIMIT 5
""")
for row in cursor.fetchall():
    print(f"📄 {row['title'][:40]} — Desc Len: {row['text_len']} — Last Seen: {row['last_seen_on_platform']}")
conn.close()

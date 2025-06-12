# agents/scraper/sources/jsearch_scraper.py

import requests
import os, sys

# DB import setup
try:
    from utils.db_utils import add_or_update_job
except ImportError:
    PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
    if PROJECT_ROOT not in sys.path:
        sys.path.insert(0, PROJECT_ROOT)
    from utils.db_utils import add_or_update_job

class JsearchScraper:
    def __init__(self, search_queries: list[str]):
        """
        Initializes the JSearch Scraper.
        Args:
            search_queries (list[str]): A list of search terms (e.g., "AI Engineer in Belgium").
        """
        self.search_queries = search_queries
        self.platform_source = "JSearch"
        self.api_url = "https://jsearch.p.rapidapi.com/search"
        self.api_key = os.getenv("JSEARCH_API_KEY")
        self.api_host = "jsearch.p.rapidapi.com"
        self.request_timeout_api = int(os.getenv("API_REQUEST_TIMEOUT", 20)) # Give API more time

    def fetch_jobs(self) -> tuple[int, int]:
        if not self.api_key:
            print("❌ JSearch API key not found in .env file. Skipping.")
            return 0, 0

        print(f"🔎 Starting JSearchScraper for {len(self.search_queries)} queries...")
        seen_count, added_count = 0, 0

        headers = {
            "X-RapidAPI-Key": self.api_key,
            "X-RapidAPI-Host": self.api_host
        }

        for query in self.search_queries:
            params = {"query": query, "num_pages": "1"}
            try:
                response = requests.get(self.api_url, headers=headers, params=params, timeout=self.request_timeout_api)
                response.raise_for_status()
                
                offers = response.json().get("data", [])
                print(f"📥 {len(offers)} offers found for query: '{query}'")

                for offer in offers:
                    # Skip jobs without an apply link or title, as they are often invalid
                    if not offer.get("job_apply_link") or not offer.get("job_title"):
                        continue
                    
                    job_data = {
                        "job_url": offer.get("job_apply_link"),
                        "platform_job_id": offer.get("job_id"),
                        "platform_source": self.platform_source,
                        "company_name": offer.get("employer_name"),
                        "title": offer.get("job_title"),
                        "location": offer.get("job_city") or offer.get("job_country"),
                        "department": None, # JSearch doesn't provide this
                        "date_posted_on_platform": offer.get("job_posted_at_datetime_utc"),
                        "api_provided_description": offer.get("job_description"),
                        "full_description_text": offer.get("job_description"),
                    }

                    status, _ = add_or_update_job(job_data)
                    if status == "inserted":
                        added_count += 1
                    seen_count += 1

            except requests.exceptions.RequestException as e:
                print(f"⚠️ HTTP error for query '{query}': {e}")
            except Exception as e:
                print(f"❌ Unexpected error for query '{query}': {type(e).__name__} - {e}")

        print(f"✅ Done. Seen: {seen_count}, Added: {added_count}")
        return seen_count, added_count

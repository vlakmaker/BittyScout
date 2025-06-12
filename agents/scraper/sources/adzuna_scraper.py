# agents/scraper/sources/adzuna_scraper.py

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

class AdzunaScraper:
    def __init__(self, search_configs: list[dict]):
        self.search_configs = search_configs
        self.platform_source = "Adzuna"
        # --- THIS IS THE CORRECTED LINE ---
        self.base_url = "https://api.adzuna.com/v1/api/jobs"
        # --- END CORRECTION ---
        self.app_id = os.getenv("ADZUNA_APP_ID")
        self.app_key = os.getenv("ADZUNA_APP_KEY")
        self.request_timeout_api = int(os.getenv("API_REQUEST_TIMEOUT", 20))

    def fetch_jobs(self) -> tuple[int, int]:
        if not self.app_id or not self.app_key:
            print("❌ Adzuna App ID or Key not found in .env file. Skipping.")
            return 0, 0

        print(f"🔎 Starting AdzunaScraper for {len(self.search_configs)} search configurations...")
        seen_count, added_count = 0, 0

        for config in self.search_configs:
            country_code = config.get("country_code", "gb")
            api_url = f"{self.base_url}/{country_code}/search/1" # Page 1
            
            params = {
                'app_id': self.app_id,
                'app_key': self.app_key,
                'what': config.get('what'),
                'where': config.get('where'),
                'results_per_page': 50,
                'content-type': 'application/json'
            }
            
            query_str = f"'{config.get('what')}' in '{config.get('where')}'"
            try:
                response = requests.get(api_url, params=params, timeout=self.request_timeout_api)
                response.raise_for_status()
                
                offers = response.json().get("results", [])
                print(f"📥 {len(offers)} offers found for query: {query_str}")

                for offer in offers:
                    job_data = {
                        "job_url": offer.get("redirect_url"),
                        "platform_job_id": offer.get("id"),
                        "platform_source": self.platform_source,
                        "company_name": offer.get("company", {}).get("display_name"),
                        "title": offer.get("title"),
                        "location": offer.get("location", {}).get("display_name"),
                        "department": offer.get("category", {}).get("label"),
                        "date_posted_on_platform": offer.get("created"),
                        "api_provided_description": offer.get("description"),
                        "full_description_text": offer.get("description"),
                    }

                    status, _ = add_or_update_job(job_data)
                    if status == "inserted":
                        added_count += 1
                    seen_count += 1

            except requests.exceptions.RequestException as e:
                print(f"⚠️ HTTP error for query {query_str}: {e}")
            except Exception as e:
                print(f"❌ Unexpected error for query {query_str}: {type(e).__name__} - {e}")

        print(f"✅ Done. Seen: {seen_count}, Added: {added_count}")
        return seen_count, added_count

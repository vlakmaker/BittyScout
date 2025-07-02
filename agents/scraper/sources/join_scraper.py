# agents/scraper/sources/join_scraper.py

import requests
import os, sys

try:
    from utils.db_utils import add_or_update_job
except ImportError:
    PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
    if PROJECT_ROOT not in sys.path:
        sys.path.insert(0, PROJECT_ROOT)
    from utils.db_utils import add_or_update_job

class JoinScraper:
    def __init__(self, search_configs: list[dict]):
        self.search_configs = search_configs
        self.platform_source = "JOIN.com"
        self.api_url = "https://api.join.com/v1/job-search/public/search"
        self.request_timeout_api = int(os.getenv("API_REQUEST_TIMEOUT", 15))
        # --- ADDED: More browser-like headers to avoid 403 Forbidden ---
        self.headers = {
            'User-Agent': os.getenv("SCRAPER_USER_AGENT", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"),
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Origin': 'https://join.com',
            'Referer': 'https://join.com/',
        }
        # --- END OF HEADER BLOCK ---

    def fetch_jobs(self) -> tuple[int, int]:
        print(f"🔎 Starting JOIN.com Scraper for {len(self.search_configs)} searches...")
        seen_count, added_count = 0, 0

        for config in self.search_configs:
            query = config.get('query', '')
            country_code = config.get('country_code', '')
            query_str = f"'{query}' in country '{country_code}'"

            params = {'keywords': query, 'country': country_code, 'page': 1, 'pageSize': 50}
            
            try:
                # Use the new headers in the request
                response = requests.get(self.api_url, params=params, headers=self.headers, timeout=self.request_timeout_api)
                response.raise_for_status()
                
                offers = response.json()
                print(f"📥 {len(offers)} offers found for query: {query_str}")

                for offer in offers:
                    job_url = f"https://join.com/companies/{offer['company']['slug']}/{offer['id']}"
                    job_data = {
                        "job_url": job_url, "platform_job_id": str(offer.get("id")),
                        "platform_source": self.platform_source, "company_name": offer.get("company", {}).get("name"),
                        "title": offer.get("title"), "location": offer.get("location", {}).get("city"),
                        "department": None, "date_posted_on_platform": offer.get("publishedAt"),
                        "api_provided_description": offer.get("description"), "full_description_text": offer.get("description"),
                    }
                    status, _ = add_or_update_job(job_data)
                    if status == "inserted": added_count += 1
                    seen_count += 1

            except requests.exceptions.RequestException as e:
                print(f"⚠️ HTTP error for query {query_str}: {e}")
            except Exception as e:
                print(f"❌ Unexpected error for query {query_str}: {type(e).__name__} - {e}")

        print(f"✅ Done. Seen: {seen_count}, Added: {added_count}")
        return seen_count, added_count
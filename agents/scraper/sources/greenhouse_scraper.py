# agents/scraper/sources/greenhouse_scraper.py

import requests
from bs4 import BeautifulSoup
import os, sys

# DB import setup (consistent with other scrapers)
try:
    from utils.db_utils import add_or_update_job
except ImportError:
    PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
    if PROJECT_ROOT not in sys.path:
        sys.path.insert(0, PROJECT_ROOT)
    from utils.db_utils import add_or_update_job

class GreenhouseScraper:
    def __init__(self, company_identifiers: list[str]):
        """
        Initializes the GreenhouseScraper.
        Args:
            company_identifiers (list[str]): A list of Greenhouse board tokens (company names).
        """
        self.company_identifiers = company_identifiers
        self.platform_source = "Greenhouse"
        self.user_agent = os.getenv("SCRAPER_USER_AGENT", "BittyScout/1.0")
        self.request_timeout_api = int(os.getenv("API_REQUEST_TIMEOUT", 10))

    def _clean_html_description(self, html_content: str) -> str:
        """Uses BeautifulSoup to convert HTML description to clean text."""
        if not html_content:
            return ""
        return BeautifulSoup(html_content, 'html.parser').get_text(separator=' ', strip=True)

    def _get_department(self, departments_list: list) -> str | None:
        """Safely extracts the first department name from the list of department objects."""
        if departments_list and isinstance(departments_list, list):
            return departments_list[0].get('name')
        return None

    def fetch_jobs(self) -> tuple[int, int]:
        print(f"🔎 Starting GreenhouseScraper for {len(self.company_identifiers)} companies...")
        seen_count, added_count = 0, 0

        for board_token in self.company_identifiers:
            api_url = f"https://api.greenhouse.io/v1/boards/{board_token}/jobs?content=true"
            try:
                response = requests.get(api_url, timeout=self.request_timeout_api, headers={'User-Agent': self.user_agent})
                response.raise_for_status()
                
                offers = response.json().get("jobs", [])
                print(f"📥 {len(offers)} offers found for {board_token}.")

                for offer in offers:
                    title = offer.get("title")
                    job_url = offer.get("absolute_url")
                    if not title or not job_url:
                        continue
                    
                    description_text = self._clean_html_description(offer.get("content"))

                    job_data = {
                        "job_url": job_url,
                        "platform_job_id": str(offer.get("id")),
                        "platform_source": self.platform_source,
                        "company_name": board_token.replace("-", " ").title(),
                        "title": title,
                        "location": offer.get("location", {}).get("name"),
                        "department": self._get_department(offer.get("departments")),
                        "date_posted_on_platform": offer.get("updated_at"),
                        # For Greenhouse, the API provides the full description.
                        "api_provided_description": description_text,
                        "full_description_text": description_text,
                    }

                    status, _ = add_or_update_job(job_data)
                    if status == "inserted":
                        added_count += 1
                    seen_count += 1

            except requests.exceptions.RequestException as e:
                print(f"⚠️ HTTP error for {board_token}: {e}")
            except Exception as e:
                print(f"❌ Unexpected error for {board_token}: {type(e).__name__} - {e}")

        print(f"✅ Done. Seen: {seen_count}, Added: {added_count}")
        return seen_count, added_count

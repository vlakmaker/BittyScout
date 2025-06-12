# agents/scraper/sources/recruitee_scraper.py

import requests
from bs4 import BeautifulSoup
from newspaper import Article, Config as NewspaperConfig
import os, sys, time
from datetime import datetime, timezone

# DB import setup (consistent with LeverScraper)
try:
    from utils.db_utils import add_or_update_job
except ImportError:
    PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
    if PROJECT_ROOT not in sys.path:
        sys.path.insert(0, PROJECT_ROOT)
    from utils.db_utils import add_or_update_job

class RecruiteeScraper:
    def __init__(self, company_identifiers: list[str]):
        self.company_identifiers = company_identifiers
        self.platform_source = "Recruitee"
        self.user_agent = os.getenv("SCRAPER_USER_AGENT", "BittyScout/1.0")
        self.request_timeout_api = int(os.getenv("API_REQUEST_TIMEOUT", 10))
        self.request_timeout_page = int(os.getenv("SCRAPER_REQUEST_TIMEOUT", 15))
        self.article_fetch_delay = float(os.getenv("ARTICLE_FETCH_DELAY_SECONDS", 2.0))

    def _fetch_full_text_newspaper3k(self, url: str) -> str:
        if not url: return ""
        try:
            config = NewspaperConfig()
            config.browser_user_agent = self.user_agent
            config.request_timeout = self.request_timeout_page
            config.fetch_images = False
            config.memoize_articles = False

            article_parser = Article(url, config=config)
            article_parser.download()
            if not article_parser.html: return ""
            article_parser.parse()
            return article_parser.text.strip() if article_parser.text else ""
        except Exception as e:
            print(f"⚠️ newspaper3k failed for {url}: {type(e).__name__} - {e}")
            return ""

    def _convert_timestamp(self, ts_str):
        if not ts_str:
            return None
        try:
            return datetime.fromisoformat(ts_str).isoformat()
        except ValueError:
            return ts_str

    def fetch_jobs(self) -> tuple[int, int]:
        print(f"🔎 Starting RecruiteeScraper for {len(self.company_identifiers)} companies...")
        seen_count, added_count = 0, 0

        for company_id in self.company_identifiers:
            api_url = f"https://{company_id}.recruitee.com/api/offers/"
            try:
                response = requests.get(api_url, timeout=self.request_timeout_api, headers={'User-Agent': self.user_agent})
                response.raise_for_status()
                offers = response.json().get("offers", [])
                print(f"📥 {len(offers)} offers found for {company_id}.")

                for offer in offers:
                    title = offer.get("title")
                    job_url = offer.get("careers_url")
                    if not title or not job_url:
                        continue

                    time.sleep(self.article_fetch_delay)
                    full_desc_text = self._fetch_full_text_newspaper3k(job_url)

                    raw_description_html = offer.get("description", "")
                    api_description_text = BeautifulSoup(raw_description_html, "html.parser").get_text(" ", strip=True)

                    job_data = {
                        "job_url": job_url,
                        "platform_job_id": str(offer.get("id")),
                        "platform_source": self.platform_source,
                        "company_name": offer.get("company_name") or company_id.replace("-", " ").title(),
                        "title": title,
                        "location": offer.get("city") or offer.get("location_str") or offer.get("location"),
                        "department": offer.get("department"),
                        "date_posted_on_platform": self._convert_timestamp(offer.get("created_at") or offer.get("published_at")),
                        "api_provided_description": api_description_text,
                        "full_description_text": full_desc_text or api_description_text
                    }

                    status, _ = add_or_update_job(job_data)
                    if status == "inserted":
                        added_count += 1
                    seen_count += 1

            except requests.exceptions.RequestException as e:
                print(f"⚠️ HTTP error for {company_id}: {e}")
            except Exception as e:
                print(f"❌ Unexpected error for {company_id}: {e}")

        print(f"✅ Done. Seen: {seen_count}, Added: {added_count}")
        return seen_count, added_count

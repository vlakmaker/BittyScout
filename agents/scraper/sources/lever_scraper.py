# agents/scraper/sources/lever_scraper.py

import requests
from bs4 import BeautifulSoup
from newspaper import Article, Config as NewspaperConfig
import os, sys, time
from datetime import datetime, timezone

# DB import setup (consistent with other scrapers)
try:
    from utils.db_utils import add_or_update_job
except ImportError:
    PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
    if PROJECT_ROOT not in sys.path:
        sys.path.insert(0, PROJECT_ROOT)
    from utils.db_utils import add_or_update_job

class LeverScraper:
    def __init__(self, company_identifiers: list[str]):
        self.company_identifiers = company_identifiers
        self.platform_source = "Lever"
        self.user_agent = os.getenv("SCRAPER_USER_AGENT", "BittyScout/1.0")
        self.request_timeout_api = int(os.getenv("API_REQUEST_TIMEOUT", 10))
        self.request_timeout_page = int(os.getenv("SCRAPER_REQUEST_TIMEOUT", 15))
        self.article_fetch_delay = float(os.getenv("ARTICLE_FETCH_DELAY_SECONDS", 2.0))

    def _fetch_full_text_newspaper3k(self, url: str) -> str:
        if not url:
            return ""
        try:
            config = NewspaperConfig()
            config.browser_user_agent = self.user_agent
            config.request_timeout = self.request_timeout_page
            config.fetch_images = False

            article = Article(url, config=config)
            article.download()
            if not article.html:
                return ""
            article.parse()
            return article.text.strip() if article.text else ""
        except Exception as e:
            print(f"⚠️ newspaper3k failed for {url}: {type(e).__name__} - {e}")
            return ""

    def _convert_ms_timestamp(self, ms_timestamp):
        if not ms_timestamp:
            return None
        try:
            return datetime.fromtimestamp(ms_timestamp / 1000, tz=timezone.utc).isoformat()
        except (ValueError, TypeError):
            return None

    def fetch_jobs(self) -> tuple[int, int]:
        print(f"🔎 Starting LeverScraper for {len(self.company_identifiers)} companies...")
        seen_count, added_count = 0, 0

        for company_id in self.company_identifiers:
            api_url = f"https://api.lever.co/v0/postings/{company_id}?mode=json"
            try:
                resp = requests.get(api_url, headers={"User-Agent": self.user_agent}, timeout=self.request_timeout_api)
                resp.raise_for_status()
                offers = resp.json()
                print(f"📥 {len(offers)} offers found for {company_id}.")

                for offer in offers:
                    job_url = offer.get("hostedUrl")
                    title = offer.get("text")
                    if not job_url or not title:
                        continue

                    time.sleep(self.article_fetch_delay)
                    full_desc_text = self._fetch_full_text_newspaper3k(job_url)

                    raw_description_html = offer.get("description", "")
                    api_description_text = BeautifulSoup(raw_description_html, "html.parser").get_text(" ", strip=True)

                    job_data = {
                        "job_url": job_url,
                        "platform_job_id": str(offer.get("id")),
                        "platform_source": self.platform_source,
                        "company_name": company_id.replace("-", " ").title(),
                        "title": title,
                        "location": offer.get("categories", {}).get("location"),
                        "department": offer.get("categories", {}).get("team"),
                        "date_posted_on_platform": self._convert_ms_timestamp(offer.get("createdAt")),
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

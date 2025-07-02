# agents/scraper/sources/wttj_scraper.py

import os, sys, time
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

try:
    from utils.db_utils import add_or_update_job
except ImportError:
    PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
    if PROJECT_ROOT not in sys.path:
        sys.path.insert(0, PROJECT_ROOT)
    from utils.db_utils import add_or_update_job

class WelcomeToTheJungleScraper:
    def __init__(self, search_configs: list[dict]):
        self.search_configs = search_configs
        self.platform_source = "WelcomeToTheJungle"
        self.base_url = "https://www.welcometothejungle.com/en/jobs"
        self.timeout = int(os.getenv("SCRAPER_REQUEST_TIMEOUT", 15))

    def fetch_jobs(self) -> tuple[int, int]:
        print(f"🔎 Starting WelcomeToTheJungleScraper for {len(self.search_configs)} queries...")
        seen_count, added_count = 0, 0

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64)")
            page = context.new_page()
            detail_page = context.new_page()

            for config in self.search_configs:
                query = config.get("query", "")
                location = config.get("location", "")
                query_str = f"'{query}' in '{location}'"

                search_url = f"{self.base_url}?query={query.replace(' ', '%20')}&aroundQuery={location}"
                print(f"🌍 Visiting: {search_url}")

                try:
                    page.goto(search_url, timeout=self.timeout * 1000)
                    page.wait_for_selector("ul[data-testid='search-results-list'] li", timeout=self.timeout * 1000)

                    job_cards = page.query_selector_all("ul[data-testid='search-results-list'] li")
                    print(f"📥 {len(job_cards)} offers found for query: {query_str}")

                    for card in job_cards:
                        try:
                            anchor = card.query_selector("a")
                            job_url = "https://www.welcometothejungle.com" + anchor.get_attribute("href") if anchor else None
                            title_elem = card.query_selector("h3")
                            company_elem = card.query_selector("span[data-testid='company-name']")
                            location_elem = card.query_selector("span[data-testid='job-location']")

                            title = title_elem.inner_text().strip() if title_elem else None
                            company = company_elem.inner_text().strip() if company_elem else None
                            location_text = location_elem.inner_text().strip() if location_elem else None

                            full_description = None
                            if job_url:
                                try:
                                    detail_page.goto(job_url, timeout=self.timeout * 1000)
                                    detail_page.wait_for_selector("div[data-testid='job-description']", timeout=self.timeout * 1000)
                                    desc_elem = detail_page.query_selector("div[data-testid='job-description']")
                                    full_description = desc_elem.inner_text().strip() if desc_elem else None
                                except PlaywrightTimeout:
                                    print(f"⚠️ Timeout fetching job detail: {job_url}")
                                except Exception as e:
                                    print(f"⚠️ Detail page error ({job_url}): {type(e).__name__} - {e}")

                            if not job_url:
                                continue

                            job_data = {
                                "job_url": job_url,
                                "platform_job_id": job_url.split('/')[-1],
                                "platform_source": self.platform_source,
                                "company_name": company,
                                "title": title,
                                "location": location_text,
                                "department": None,
                                "date_posted_on_platform": None,
                                "api_provided_description": full_description,
                                "full_description_text": full_description,
                            }

                            status, _ = add_or_update_job(job_data)
                            if status == "inserted":
                                added_count += 1
                            seen_count += 1
                        except Exception as e:
                            print(f"⚠️ Error parsing job card: {type(e).__name__} - {e}")

                except PlaywrightTimeout:
                    print(f"⚠️ Timeout when fetching query: {query_str}")
                except Exception as e:
                    print(f"❌ Unexpected error for query {query_str}: {type(e).__name__} - {e}")

            browser.close()
        print(f"✅ Done. Seen: {seen_count}, Added: {added_count}")
        return seen_count, added_count

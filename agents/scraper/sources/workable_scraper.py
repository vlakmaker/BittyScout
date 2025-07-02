# agents/scraper/sources/workable_scraper.py

from bs4 import BeautifulSoup
import os, sys, time
from playwright.sync_api import sync_playwright

try:
    from utils.db_utils import add_or_update_job
except ImportError:
    PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
    if PROJECT_ROOT not in sys.path:
        sys.path.insert(0, PROJECT_ROOT)
    from utils.db_utils import add_or_update_job

class WorkableScraper:
    def __init__(self, company_identifiers: list[str]):
        self.company_identifiers = company_identifiers
        self.platform_source = "Workable"
        timeout_sec = int(os.getenv("SCRAPER_REQUEST_TIMEOUT", 20))
        self.playwright_timeout_ms = timeout_sec * 1000

    def fetch_jobs(self) -> tuple[int, int]:
        print(f"🔎 Starting WorkableScraper (Playwright) for {len(self.company_identifiers)} companies...")
        seen_count, added_count = 0, 0

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            for company_slug in self.company_identifiers:
                list_url = f"https://apply.workable.com/{company_slug}/"
                try:
                    page.goto(list_url, timeout=self.playwright_timeout_ms)
                    # ✅ Updated selector based on actual HTML structure
                    page.wait_for_selector('ul[data-ui="list"] li[data-ui="job"]', state='visible', timeout=10000)
                    
                    html_content = page.content()
                    soup = BeautifulSoup(html_content, 'html.parser')
                    
                    # ✅ Updated to match actual job listing structure
                    job_elements = soup.select('li[data-ui="job"]')
                    print(f"📥 {len(job_elements)} offers found for {company_slug}.")

                    for job_el in job_elements:
                        title_tag = job_el.find('h3')
                        link_tag = job_el.find('a')
                        location_tag = job_el.find('span', attrs={'data-ui': 'job-location'})

                        if not all([title_tag, link_tag]):
                            continue

                        title = title_tag.get_text(strip=True)
                        relative_url = link_tag.get('href', '')
                        job_url = f"https://apply.workable.com{relative_url}"
                        location = location_tag.get_text(strip=True) if location_tag else None

                        job_data = {
                            "job_url": job_url,
                            "platform_job_id": relative_url.strip('/').split('/')[-1],
                            "platform_source": self.platform_source,
                            "company_name": company_slug.replace("-", " ").title(),
                            "title": title,
                            "location": location,
                            "department": None,
                            "date_posted_on_platform": None,
                            "api_provided_description": title,
                            "full_description_text": title,
                        }

                        status, _ = add_or_update_job(job_data)
                        if status == "inserted":
                            added_count += 1
                        seen_count += 1

                except Exception as e:
                    print(f"❌ Playwright error for {company_slug}: {type(e).__name__} - {e}")
            
            browser.close()

        print(f"✅ Done. Seen: {seen_count}, Added: {added_count}")
        return seen_count, added_count

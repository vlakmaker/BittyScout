# agents/scraper/sources/personio_scraper.py

import requests
import xml.etree.ElementTree as ET
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

class PersonioScraper:
    def __init__(self, company_identifiers: list[str]):
        self.company_identifiers = company_identifiers
        self.platform_source = "Personio"
        self.user_agent = os.getenv("SCRAPER_USER_AGENT", "BittyScout/1.0")
        self.request_timeout_api = int(os.getenv("API_REQUEST_TIMEOUT", 15)) # Give XML a bit more time
        # Note: No article_fetch_delay or request_timeout_page needed, as the XML feed contains all data.

    def _get_text(self, element, tag):
        """Safely gets text from a child node of an XML element."""
        node = element.find(tag)
        return node.text.strip() if node is not None and node.text else None

    def _extract_description(self, position_element):
        """Extracts and cleans the job description from the XML, which is often nested HTML in a CDATA block."""
        job_desc_node = position_element.find('jobDescriptions')
        if job_desc_node is None:
            return ""

        for desc in job_desc_node.findall('jobDescription'):
            value_node = desc.find('value')
            if value_node is not None and value_node.text:
                # The description is HTML; use BeautifulSoup to get clean text.
                return BeautifulSoup(value_node.text, 'html.parser').get_text(separator=' ', strip=True)
        return ""

    def fetch_jobs(self) -> tuple[int, int]:
        print(f"🔎 Starting PersonioScraper for {len(self.company_identifiers)} companies...")
        seen_count, added_count = 0, 0

        for company_id in self.company_identifiers:
            # Personio's XML feed URL format. '.de' is a common TLD for them.
            xml_feed_url = f"https://{company_id}.jobs.personio.de/xml"
            try:
                response = requests.get(xml_feed_url, timeout=self.request_timeout_api, headers={'User-Agent': self.user_agent})
                response.raise_for_status()
                
                # Decode content to handle special characters before parsing
                root = ET.fromstring(response.content.decode('utf-8'))
                
                positions = root.findall('position')
                print(f"📥 {len(positions)} offers found for {company_id}.")

                for position in positions:
                    job_id = self._get_text(position, 'id')
                    title = self._get_text(position, 'name')
                    if not job_id or not title:
                        continue

                    # The job URL is not in the feed, so we construct it.
                    job_url = f"https://{company_id}.jobs.personio.de/job/{job_id}"
                    description_text = self._extract_description(position)

                    job_data = {
                        "job_url": job_url,
                        "platform_job_id": job_id,
                        "platform_source": self.platform_source,
                        "company_name": company_id.replace("-", " ").title(),
                        "title": title,
                        "location": self._get_text(position, 'office'),
                        "department": self._get_text(position, 'department'),
                        "date_posted_on_platform": self._get_text(position, 'creationDate'),
                        # For Personio, the API description is the full description.
                        "api_provided_description": description_text,
                        "full_description_text": description_text,
                    }

                    status, _ = add_or_update_job(job_data)
                    if status == "inserted":
                        added_count += 1
                    seen_count += 1

            except requests.exceptions.RequestException as e:
                print(f"⚠️ HTTP error for {company_id} at {xml_feed_url}: {e}")
            except ET.ParseError as e:
                print(f"❌ XML parsing error for {company_id}. The feed may be invalid or unavailable.")
            except Exception as e:
                print(f"❌ Unexpected error for {company_id}: {type(e).__name__} - {e}")

        print(f"✅ Done. Seen: {seen_count}, Added: {added_count}")
        return seen_count, added_count

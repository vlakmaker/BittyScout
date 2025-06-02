# agents/scraper/workable_scraper.py

import requests
from typing import List, Dict

def scrape_workable_jobs() -> List[Dict]:
    print("🔎 WorkableScraper: Searching for companies...")

    known_workable_companies = [
        "novemberfive", "dataroots", "unifly", "intigriti", "ogone"
    ]

    jobs = []
    for company in known_workable_companies:
        try:
            url = f"https://{company}.workable.com/api/v1/jobs"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()

            for job in data.get("jobs", []):
                title = job.get("title")
                location = job.get("location", {}).get("location")
                job_url = job.get("url") or f"https://{company}.workable.com"
                description = job.get("description") or job.get("short_description") or "No description provided."

                if not title or not job_url:
                    continue

                jobs.append({
                    "title": title,
                    "company": company.capitalize(),
                    "location": location,
                    "url": job_url,
                    "description": description,
                    "source": "Workable",
                })

        except Exception as e:
            print(f"⚠️  Failed to scrape {company}.workable.com: {e}")

    return jobs

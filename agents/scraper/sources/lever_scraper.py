# agents/scraper/lever_scraper.py

import requests
from typing import List, Dict

def scrape_lever_jobs() -> List[Dict]:
    print("🔎 LeverScraper: Searching for companies...")

    known_lever_companies = [
        "deliverect", "silverfin", "intigriti", "channable"
    ]

    jobs = []
    for company in known_lever_companies:
        try:
            url = f"https://api.lever.co/v0/postings/{company}?mode=json"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()

            for job in data:
                title = job.get("text")
                location = job.get("categories", {}).get("location")
                job_url = job.get("hostedUrl")
                description = job.get("description") or "No description provided."

                if not title or not job_url:
                    continue

                jobs.append({
                    "title": title,
                    "company": company.capitalize(),
                    "location": location,
                    "url": job_url,
                    "description": description,
                    "source": "Lever",
                })

        except Exception as e:
            print(f"⚠️  Failed to scrape {company} on Lever: {e}")

    return jobs

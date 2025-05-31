# agents/scraper/recruitee_scraper.py

import requests
from typing import List, Dict

def scrape_recruitee_jobs() -> List[Dict]:
    print("🔎 RecruiteeScraper: Searching for companies...")

    known_companies = [
        "deliverect", "teamleader", "novemberfive", "onetribe", "visma", "channable",
        "silverfin", "showpad", "abo", "mealhero", "faktionbv1"
    ]

    jobs = []
    for company in known_companies:
        try:
            url = f"https://{company}.recruitee.com/api/offers/"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()

            for offer in data.get("offers", []):
                title = offer.get("title")
                location = offer.get("city")
                job_url = offer.get("careers_url") or offer.get("url")
                description = offer.get("description", "No description provided.")
                company_name = offer.get("company_name") or company.capitalize()

                if not title or not job_url:
                    continue

                jobs.append({
                    "title": title,
                    "company": company_name,
                    "location": location,
                    "url": job_url,
                    "description": description,
                    "source": "Recruitee",
                })

        except Exception as e:
            print(f"⚠️  Failed to scrape {company}.recruitee.com: {e}")

    return jobs

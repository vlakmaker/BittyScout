# agents/scraper/scraper_agent.py

from typing import List, Dict
from agents.scraper.sources.recruitee_scraper import scrape_recruitee_jobs
from agents.scraper.sources.lever_scraper import scrape_lever_jobs
from agents.scraper.sources.workable_scraper import scrape_workable_jobs

class ScraperAgent:
    def __init__(self):
        pass

    def get_jobs(self) -> List[Dict]:
        print("🌐 ScraperAgent: Collecting jobs from supported boards...")

        # Recruitee Jobs
        recruitee_jobs = scrape_recruitee_jobs()
        print(f"✅ Recruitee: Found {len(recruitee_jobs)} job(s)")

        # Workable Jobs
        workable_jobs = scrape_workable_jobs()
        print(f"✅ Workable: Found {len(workable_jobs)} job(s)")

        # Lever Jobs
        lever_jobs = scrape_lever_jobs()
        print(f"✅ Lever: Found {len(lever_jobs)} job(s)")

        # Combine all jobs into one list
        all_jobs = recruitee_jobs + workable_jobs + lever_jobs
        return all_jobs

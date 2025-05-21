# agents/scraper/scraper_agent.py

from typing import List, Dict

class ScraperAgent:
    def __init__(self):
        pass

    def get_jobs(self) -> List[Dict]:
        # In the future, this will scrape real websites or use APIs
        print("🌐 ScraperAgent: Generating mock job listings...")

        jobs = [
            {
                "title": "AI Research Engineer",
                "company": "OpenAI",
                "location": "Remote",
                "description": "Work on state-of-the-art generative models.",
                "url": "https://example.com/job/openai-ai-research"
            },
            {
                "title": "Product Manager - AI",
                "company": "Anthropic",
                "location": "Remote",
                "description": "Lead product for large-scale language model services.",
                "url": "https://example.com/job/anthropic-pm"
            },
            {
                "title": "Full Stack Developer",
                "company": "Startup Inc.",
                "location": "New York, NY",
                "description": "Develop and maintain web applications.",
                "url": "https://example.com/job/startup-dev"
            }
        ]

        return jobs

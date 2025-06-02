# agents/manager/manager_agent.py

from agents.scraper.scraper_agent import ScraperAgent
from agents.matcher.matcher_agent import MatcherAgent
from agents.scorer.scorer_agent import ScorerAgent
from agents.output.output_agent import OutputAgent
from agents.summarizer.summarizer_agent import SummarizerAgent
from agents.notifier.email_agent import EmailAgent


class ManagerAgent:
    def __init__(self):
        self.scraper = ScraperAgent()
        self.matcher = MatcherAgent()
        self.scorer = ScorerAgent()
        self.output = OutputAgent()
        self.summarizer = SummarizerAgent()

    def run(self):
        print("🎩 ManagerAgent: Starting job flow...")

        # 1. Scrape jobs (mock)
        job_listings = self.scraper.get_jobs()
        print(f"🌐 ScraperAgent: Fetched {len(job_listings)} job(s)")
            
        # 2. Match/filter jobs
        matched_jobs = self.matcher.match(job_listings)
        print(f"🧲 MatcherAgent: Matched {len(matched_jobs)} job(s)")

        # 3. Score/filter jobs
        scored_jobs = self.scorer.score_jobs(matched_jobs)
        print(f"🧠 ScorerAgent: Scored {len(scored_jobs)} job(s)")

        # 4. Summarize jobs
        summarized_jobs = self.summarizer.summarize_jobs(scored_jobs)
        print(f"📝 SummarizerAgent: Summarized {len(summarized_jobs)} job(s)")

        # 5. Output results
        self.output.display(summarized_jobs)

        # 6. Email results
        email_agent = EmailAgent()
        email_agent.send_email(summarized_jobs)

        print("🎩 ManagerAgent: Flow complete.")

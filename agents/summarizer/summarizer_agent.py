# agents/summarizer/summarizer_agent.py

from typing import List, Dict
from utils.llm_utils import call_llm

class SummarizerAgent:
    def __init__(self):
        self.system_prompt = "You are a helpful assistant that summarizes job listings for an AI professional."

    def summarize_jobs(self, jobs: List[Dict]) -> List[Dict]:
        summaries = []

        for job in jobs:
            text = f"{job['title']} at {job['company']}\nLocation: {job['location']}\nDescription: {job['description']}"

            prompt = (
                "Summarize this job in 3 bullet points:\n"
                "• What is the role?\n"
                "• Why might it be a fit for someone interested in AI/strategy/remote?\n"
                "• Any concerns or missing info?\n\n"
                f"{text}"
            )

            summary = call_llm(prompt, self.system_prompt)
            job_copy = job.copy()
            job_copy["summary"] = summary
            summaries.append(job_copy)

        return summaries

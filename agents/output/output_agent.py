# agents/output/output_agent.py

import json
import os
from utils.job_cache import JobCache

class OutputAgent:
    def __init__(self, save_to_file: bool = True):
        self.output_path = "outputs/jobs_output.json"
        os.makedirs(os.path.dirname(self.output_path), exist_ok=True)
        self.save_to_file = save_to_file
        self.cache = JobCache()

    def display(self, jobs):  # ← FIXED: now indented inside the class
        fresh_jobs = []
        for job in jobs:
            if not self.cache.is_seen(job):
                fresh_jobs.append(job)
                self.cache.mark_sent(job)

        if not fresh_jobs:
            print("📭 No new jobs today.")
            return

        print("\n🎯 Matched Job Results:\n")
        for i, job in enumerate(fresh_jobs, 1):
            try:
                print(f"{i}. {job['title']} at {job['company']}")
                print(f"   📍 Location: {job.get('location', 'N/A')}")
                print(f"   🔗 Link: {job['url']}\n")
            except KeyError as e:
                print(f"❌ Skipping malformed job at index {i} due to missing field: {e}")
                print(f"Job data: {job}\n")

        if self.save_to_file:
            with open(self.output_path, "w") as f:
                json.dump(fresh_jobs, f, indent=2)
            print(f"💾 Jobs saved to: {self.output_path}")


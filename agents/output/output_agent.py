# agents/output/output_agent.py

import json
import os

class OutputAgent:
    def __init__(self, save_to_file: bool = True):
        self.output_path = "outputs/jobs_output.json"
        os.makedirs(os.path.dirname(self.output_path), exist_ok=True)
        self.save_to_file = save_to_file

    def display(self, jobs):
        print("\n🎯 Matched Job Results:\n")

        for i, job in enumerate(jobs, 1):
            print(f"{i}. {job['title']} at {job['company']}")
            print(f"   📍 Location: {job.get('location', 'N/A')}")
            print(f"   🔗 Link: {job['url']}\n")

        if self.save_to_file:
            with open(self.output_path, "w") as f:
                json.dump(jobs, f, indent=2)
            print(f"💾 Jobs saved to: {self.output_path}")

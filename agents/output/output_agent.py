# agents/output/output_agent.py

from typing import List, Dict

class OutputAgent:
    def display(self, jobs: List[Dict]):
        print("\n📋 BittyScout Job Recommendations:\n")
        for i, job in enumerate(jobs, 1):
            print(f"### {i}. {job['title']} at {job['company']}")
            print(f"- 🌍 Location: {job['location']}")
            print(f"- 🔗 [View Job]({job['url']})")
            print(f"- 🧠 Score: {job['score']}")
            print(f"- 📄 {job['description']}")
            if "summary" in job:
                print("\n📝 Summary:")
                print(job['summary'])
            print("\n---\n")

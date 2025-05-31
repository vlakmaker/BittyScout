import json
from typing import List, Dict

class MatcherAgent:
    def __init__(self, config_path="config/matcher_config.json"):
        with open(config_path, "r") as f:
            self.criteria = json.load(f)

    def match(self, jobs: List[Dict]) -> List[Dict]:
        print("🧲 MatcherAgent: Filtering jobs with defined criteria...")

        keywords = [kw.lower() for kw in self.criteria.get("keywords", [])]
        locations = [loc.lower() for loc in self.criteria.get("locations", [])]
        max_remote_days = self.criteria.get("remote_days_max", 3)

        matched = []

        for job in jobs:
            title = (job.get("title") or "").lower()
            description = (job.get("description") or "").lower()
            location = (job.get("location") or "").lower()

            keyword_match = any(k in title or k in description for k in keywords)
            location_match = any(l in location for l in locations)
            remote_friendly = "remote" in location or "hybrid" in location or max_remote_days >= 3

            if keyword_match and location_match and remote_friendly:
                matched.append(job)

        return matched

import json
import os
import hashlib

class JobCache:
    def __init__(self, cache_path="outputs/job_cache.json"):
        self.cache_path = cache_path
        self.seen_jobs = set()
        self._load()

    def _load(self):
        if os.path.exists(self.cache_path):
            with open(self.cache_path, "r") as f:
                self.seen_jobs = set(json.load(f))
        else:
            self.seen_jobs = set()

    def is_seen(self, job):
        return job["url"] in self.seen_jobs

    def mark_sent(self, job):
        self.seen_jobs.add(job["url"])
        self._save()

    def _save(self):
        with open(self.cache_path, "w") as f:
            json.dump(list(self.seen_jobs), f, indent=2)


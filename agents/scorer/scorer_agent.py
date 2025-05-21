# agents/scorer/scorer_agent.py

from typing import List, Dict
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

class ScorerAgent:
    def __init__(self):
        self.model = SentenceTransformer("all-MiniLM-L6-v2")
        self.user_profile = "remote AI research, strategy, GenAI, product innovation"
        self.profile_embedding = self.model.encode([self.user_profile])

    def score_jobs(self, jobs: List[Dict]) -> List[Dict]:
        job_texts = [
            f"{job['title']} {job['description']} {job['location']}" for job in jobs
        ]
        job_embeddings = self.model.encode(job_texts)
        similarities = cosine_similarity(job_embeddings, self.profile_embedding).flatten()

        scored = []
        for job, sim in zip(jobs, similarities):
            job_copy = job.copy()
            job_copy["score"] = round(float(sim), 4)
            scored.append(job_copy)

        scored.sort(key=lambda x: x["score"], reverse=True)
        return scored

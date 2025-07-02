from dotenv import load_dotenv
load_dotenv()

from agents.notifier.discord_agent import DiscordAgent
from utils.db_utils import get_new_relevant_jobs

dummy_jobs = [
    {
        "title": "AI Product Strategist",
        "company": "Bitty Inc.",
        "location": "Remote",
        "url": "https://bittygpt.com/jobs/ai-strategist"
    },
    {
        "title": "RAG Developer",
        "company": "Groq Labs",
        "location": "Antwerp",
        "url": "https://groq.dev/jobs/rag-dev"
    }
]

agent = DiscordAgent()
agent.send_job_digest(dummy_jobs)  # or .send_discord_message(dummy_jobs)

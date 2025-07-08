# FILE: ~/BittyScout/logic.py

import os
import sys
import argparse
from dotenv import load_dotenv

# --- Project Setup ---
load_dotenv()
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
# --- End Setup ---

from agents.scraper.scraper_agent import ScraperAgent
from agents.filter.filter_agent import FilterAgent
from agents.notifier.notifier_agent import NotifierAgent
from utils.db_utils import create_jobs_table_if_not_exist
from utils.llm_utils import call_llm, list_available_models, set_model

# --- Core Functions for Each Agent ---

def run_scraping(source=None):
    """Initializes the DB and runs the scraper agent."""
    create_jobs_table_if_not_exist()
    agent = ScraperAgent()
    agent.run_scrapers(target_source=source)

def run_filtering():
    """Initializes the DB and runs the filter agent."""
    create_jobs_table_if_not_exist()
    agent = FilterAgent()
    agent.run()

def run_notification(channel="console"):
    """Runs the notifier agent to display or send a digest of relevant jobs."""
    create_jobs_table_if_not_exist()
    agent = NotifierAgent()
    agent.run(channel=channel)

# --- The Main Pipeline Function ---

def run_full_pipeline():
    """Runs the full end-to-end pipeline: scrape, filter, and notify to console."""
    print("--- 🏁 BittyScout Full Pipeline Starting ---")
    run_scraping()
    run_filtering()
    run_notification(channel="console") # Default to console output for the full run
    print("\n--- ✅ BittyScout Full Pipeline Complete ---")
    print("To send the digest via email, run: python logic.py notify --channel=email")

# (The rest of your argparse and if __name__ == "__main__" can stay here for manual runs)
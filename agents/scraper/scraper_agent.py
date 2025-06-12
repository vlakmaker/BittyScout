# agents/scraper/scraper_agent.py

import os
import yaml
from datetime import datetime

# --- Import all available scrapers ---
from agents.scraper.sources.recruitee_scraper import RecruiteeScraper
from agents.scraper.sources.lever_scraper import LeverScraper
from agents.scraper.sources.greenhouse_scraper import GreenhouseScraper
from agents.scraper.sources.adzuna_scraper import AdzunaScraper
# Add new scrapers here as you build them

# --- Bitty's Scraper Registry ---
SCRAPER_REGISTRY = {
    "Recruitee": RecruiteeScraper,
    "Lever": LeverScraper,
    "Greenhouse": GreenhouseScraper,
    "Adzuna": AdzunaScraper,
    # "JSearch": JsearchScraper, # Add when ready
    # "Personio": PersonioScraper, # Add when ready
}

class ScraperAgent:
    def __init__(self, config_path="config/job_sources.yml"):
        self.project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
        self.config_path = os.path.join(self.project_root, config_path)
        self.sources = self._load_sources()

    def _load_sources(self):
        # ... (this function remains the same)
        print(f"📄 Loading job sources from: {self.config_path}")
        try:
            with open(self.config_path, 'r') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            print(f"❌ Error: Configuration file not found at {self.config_path}")
            return {}
        except yaml.YAMLError as e:
            print(f"❌ Error parsing YAML file: {e}")
            return {}

    def run_scrapers(self, target_source=None):
        if not self.sources:
            print("🚫 No sources configured to scrape. Exiting.")
            return

        print(f"\n--- 🚀 Starting Scraper Agent at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ---")
        total_seen, total_added = 0, 0

        # Determine which sources to run based on the target_source argument
        sources_to_run = self.sources
        if target_source:
            if target_source in self.sources:
                sources_to_run = {target_source: self.sources[target_source]}
            else:
                print(f"⚠️ Source '{target_source}' not found in configuration. Available: {list(self.sources.keys())}")
                return

        for source_name, identifiers in sources_to_run.items():
            if source_name not in SCRAPER_REGISTRY:
                print(f"\n--- ⏩ Skipping '{source_name}': Scraper not found in registry. ---")
                continue

            print(f"\n--- ▶️  Running Scraper: {source_name} ---")
            ScraperClass = SCRAPER_REGISTRY[source_name]
            
            try:
                scraper_instance = ScraperClass(identifiers)
                seen, added = scraper_instance.fetch_jobs()
                total_seen += seen
                total_added += added
            except Exception as e:
                print(f"❌ An unexpected CRITICAL error occurred while running the {source_name} scraper: {e}")
        
        print(f"\n--- ✅ Scraper Agent Finished. Total Seen: {total_seen}, Total Added: {total_added} ---")

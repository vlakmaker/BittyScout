# main.py
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
from utils.db_utils import create_jobs_table_if_not_exist
from utils.llm_utils import call_llm, list_available_models, set_model # Keep for debugging

def run_scraping(source=None):
    """Initializes the DB and runs the scraper agent for all or a specific source."""
    create_jobs_table_if_not_exist()
    agent = ScraperAgent()
    agent.run_scrapers(target_source=source)

def run_filtering():
    """Initializes the DB and runs the filter agent."""
    create_jobs_table_if_not_exist()
    agent = FilterAgent()
    agent.run()

def run_full_pipeline():
    """Runs the full end-to-end pipeline: scrape then filter."""
    print("--- 🏁 BittyScout Full Pipeline Starting ---")
    run_scraping()
    run_filtering()
    print("--- ✅ BittyScout Full Pipeline Complete ---")

def run_prompt_util(prompt, model=None, system=""):
    """Utility to directly query the LLM."""
    if model: set_model(model)
    print("📝 Prompt:", prompt)
    print("\n💬 Response:")
    print(call_llm(prompt, system))

def main():
    parser = argparse.ArgumentParser(description="🤖 BittyScout - Your AI Job Scout")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # --- Main Commands ---
    run_parser = subparsers.add_parser("run", help="Run the full pipeline: scrape all jobs then filter them.")
    
    scrape_parser = subparsers.add_parser("scrape", help="Run only the scraping agents.")
    scrape_parser.add_argument("--source", type=str, help="Optionally run a single source (e.g., Greenhouse, Adzuna). Must match a key in job_sources.yml.")
    
    filter_parser = subparsers.add_parser("filter", help="Run only the filtering agent on unprocessed jobs.")

    # --- Utility Commands ---
    prompt_parser = subparsers.add_parser("prompt", help="Send a single prompt to the configured LLM.")
    prompt_parser.add_argument("prompt", type=str, help="The prompt to send.")
    prompt_parser.add_argument("--model", type=str, help="Temporarily use a specific OpenRouter model.")
    prompt_parser.add_argument("--system", type=str, default="", help="An optional system prompt.")
    
    subparsers.add_parser("list-models", help="List available LLM models from OpenRouter.")

    args = parser.parse_args()

    if args.command == "run":
        run_full_pipeline()
    elif args.command == "scrape":
        run_scraping(source=args.source)
    elif args.command == "filter":
        run_filtering()
    elif args.command == "prompt":
        run_prompt_util(args.prompt, model=args.model, system=args.system)
    elif args.command == "list-models":
        list_available_models()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()

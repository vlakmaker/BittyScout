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
    print("To send the digest via email, run: python main.py notify --channel=email")

# --- Utility Functions ---

def run_prompt_util(prompt, model=None, system=""):
    """Utility to directly query the LLM."""
    if model: set_model(model) # Note: set_model is conceptual in our current llm_utils
    print("📝 Prompt:", prompt)
    print("\n💬 Response:")
    print(call_llm(prompt, system_prompt=system))

# --- Main CLI Orchestrator ---

def main():
    parser = argparse.ArgumentParser(
        description="🤖 BittyScout - Your Personal AI Job Scout",
        formatter_class=argparse.RawTextHelpFormatter # For better help text formatting
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # --- Main Commands ---
    run_parser = subparsers.add_parser(
        "run", 
        help="Run the full pipeline: scrape -> filter -> notify (to console)."
    )
    
    scrape_parser = subparsers.add_parser(
        "scrape", 
        help="Run only the scraping agents to fetch new jobs."
    )
    scrape_parser.add_argument(
        "--source", 
        type=str, 
        help="Optionally run a single source (e.g., Greenhouse)."
    )
    
    filter_parser = subparsers.add_parser(
        "filter", 
        help="Run only the filtering agent on unprocessed jobs."
    )

    notify_parser = subparsers.add_parser(
        "notify", 
        help="Generate a digest of new, relevant jobs."
    )
    notify_parser.add_argument(
        "--channel", 
        type=str, 
        default="console", 
        choices=["console", "email"], 
        help="Output channel (default: console)."
    )

    # --- Utility Commands ---
    prompt_parser = subparsers.add_parser(
        "prompt", 
        help="Send a single prompt to the configured LLM for testing."
    )
    prompt_parser.add_argument("prompt", type=str, help="The prompt to send.")
    prompt_parser.add_argument("--model", type=str, help="Temporarily use a specific OpenRouter model override.")
    prompt_parser.add_argument("--system", type=str, default="", help="An optional system prompt.")
    
    subparsers.add_parser(
        "list-models", 
        help="List available LLM models from OpenRouter."
    )

    args = parser.parse_args()

    # --- Command Execution Logic ---
    if args.command == "run":
        run_full_pipeline()
    elif args.command == "scrape":
        run_scraping(source=args.source)
    elif args.command == "filter":
        run_filtering()
    elif args.command == "notify":
        run_notification(channel=args.channel)
    elif args.command == "prompt":
        # Note: The llm_utils `call_llm` needs the override arguments to be passed for this to work.
        # This is a debug tool, so we can enhance it later if needed.
        run_prompt_util(args.prompt, model=args.model, system=args.system)
    elif args.command == "list-models":
        list_available_models()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()

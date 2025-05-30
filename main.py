# main.py

import sys, os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import sys
import os
import argparse

from dotenv import load_dotenv
load_dotenv()

print("Python executable:", sys.executable)
print("PYTHONPATH:", os.environ.get("PYTHONPATH"))

from agents.manager.manager_agent import ManagerAgent
from agents.summarizer.summarizer_agent import SummarizerAgent
from utils.llm_utils import call_llm, list_available_models, set_model

def run_agent():
    print("🔍 BittyScout is starting...")
    manager = ManagerAgent()
    manager.run()
    print("✅ BittyScout has finished this run.")

def run_prompt(prompt, model=None, system=""):
    if model:
        set_model(model)
    print("📝 Prompt:", prompt)
    print("💬 Response:")
    print(call_llm(prompt, system))

def main():
    parser = argparse.ArgumentParser(description="🤖 BittyScout - Your AI Job Scout")
    subparsers = parser.add_subparsers(dest="command")

    # Run the full agent
    subparsers.add_parser("agent", help="Run BittyScout job discovery agent")

    # Run an LLM prompt
    run_parser = subparsers.add_parser("run", help="Send a prompt to LLM")
    run_parser.add_argument("prompt", type=str, help="Prompt to send")
    run_parser.add_argument("--model", type=str, help="OpenRouter model name")
    run_parser.add_argument("--system", type=str, default="", help="Optional system prompt")

    # List available models
    subparsers.add_parser("list-models", help="List supported models")

    args = parser.parse_args()

    if args.command == "agent":
        run_agent()

    elif args.command == "run":
        run_prompt(args.prompt, model=args.model, system=args.system)

    elif args.command == "list-models":
        list_available_models()

    else:
        parser.print_help()

if __name__ == "__main__":
    main()

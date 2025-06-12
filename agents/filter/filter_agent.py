# agents/filter/filter_agent.py

import os
import sys
import json
import re  # Import the regular expression module

# DB and LLM utils import setup
try:
    from utils.db_utils import get_unprocessed_jobs, update_job_analysis
    from utils.llm_utils import call_llm
except ImportError:
    PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    if PROJECT_ROOT not in sys.path:
        sys.path.insert(0, PROJECT_ROOT)
    from utils.db_utils import get_unprocessed_jobs, update_job_analysis
    from utils.llm_utils import call_llm

class FilterAgent:
    def __init__(self):
        """Initializes the FilterAgent with a two-stage LLM process."""
        self.triage_prompt = self._load_prompt('triage_prompt.txt')
        self.analysis_prompt = self._load_prompt('filter_prompt.txt')
        
        self.triage_model = os.getenv("TRIAGE_MODEL", "llama3-8b-8192")
        self.analysis_model = os.getenv("ANALYSIS_MODEL", "llama3-70b-8192")

    def _load_prompt(self, filename: str) -> str:
        """Loads a prompt from a file."""
        prompt_path = os.path.join(os.path.dirname(__file__), filename)
        try:
            with open(prompt_path, 'r') as f:
                return f.read()
        except FileNotFoundError:
            print(f"❌ CRITICAL: Prompt file not found at {prompt_path}")
            return ""

    def _run_triage(self, job_title: str, description_summary: str) -> bool:
        """Runs the first-pass triage to see if a job is technical."""
        if not self.triage_prompt: return False
        triage_input = f"Title: {job_title}\n\nDescription Summary: {description_summary}"
        
        response = call_llm(
            prompt=triage_input,
            system_prompt=self.triage_prompt,
            primary_groq_model_override=self.triage_model
        ).lower().strip()
        
        return response == 'true'

    def _run_deep_analysis(self, full_description: str) -> dict:
        """Runs the second-pass analysis for a detailed score and tags."""
        if not self.analysis_prompt or not full_description:
            return {'is_relevant': False, 'relevance_score': 0.0, 'tags': [], 'reasoning': 'Missing prompt or description.'}

        response_str = call_llm(
            prompt=full_description,
            system_prompt=self.analysis_prompt,
            primary_groq_model_override=self.analysis_model
        )

        try:
            # --- IMPROVED JSON PARSING LOGIC ---
            # Use regex to find a JSON object within ```json ... ``` or the whole string
            json_match = re.search(r'\{.*\}', response_str, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                return json.loads(json_str)
            else:
                # If no JSON object is found via regex, raise an error to be caught below
                raise json.JSONDecodeError("No JSON object found in LLM response", response_str, 0)
            # --- END IMPROVEMENT ---
        except (json.JSONDecodeError, TypeError):
            print(f"⚠️ LLM did not return valid JSON for deep analysis. Response:\n---\n{response_str}\n---")
            return {'is_relevant': False, 'relevance_score': 0.0, 'tags': [], 'reasoning': 'LLM output was not valid JSON.'}

    def run(self):
        print("\n--- 🕵️ Starting Filter Agent (Two-Stage LLM) ---")
        jobs_to_process = get_unprocessed_jobs()
        
        if not jobs_to_process:
            print("✅ No new jobs to process. All up to date.")
            return

        print(f"🔎 Found {len(jobs_to_process)} new jobs to analyze...")
        
        triage_passed_count = 0
        relevant_count = 0
        
        for i, job in enumerate(jobs_to_process):
            print(f"\nProcessing job {i+1}/{len(jobs_to_process)} (ID: {job['id']})...")
            job_id = job['id']
            title = job['title']
            full_desc = job['full_description_text'] or ""
            desc_summary = (job['api_provided_description'] or full_desc)[:500]

            # Stage 1: Triage
            print("  - Running Triage...", end="", flush=True)
            is_tech_role = self._run_triage(title, desc_summary)
            
            if not is_tech_role:
                print(" ❌ Not a tech role. Discarding.")
                update_job_analysis(job_id, is_relevant=False, relevance_score=0.0, tags="non-tech")
                continue
            
            print(" ✅ Tech role detected.")
            triage_passed_count += 1

            # Stage 2: Deep Analysis
            print("  - Running Deep Analysis...", end="", flush=True)
            analysis_result = self._run_deep_analysis(full_desc)
            
            is_relevant = analysis_result.get('is_relevant', False)
            score = analysis_result.get('relevance_score', 0.0)
            tags = analysis_result.get('tags', [])
            reasoning = analysis_result.get('reasoning', 'No reasoning provided.')

            tags_str = ",".join(sorted(tags))
            update_job_analysis(job_id, is_relevant, score, tags_str)
            
            if is_relevant:
                relevant_count += 1
                print(f" ✅ Relevant! (Score: {score})")
            else:
                print(f" ❌ Not a fit. (Reason: {reasoning})")
        
        print("\n--- Filter Agent Summary ---")
        print(f"Total jobs processed: {len(jobs_to_process)}")
        print(f"Passed Triage (Tech Roles): {triage_passed_count}")
        print(f"Marked as Relevant (Final): {relevant_count}")
        print("--- Filter Agent Complete ---")

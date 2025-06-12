# utils/llm_utils.py
import os
import requests
import json
import time
from dotenv import load_dotenv

# --- Environment Variable Loading ---
dotenv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '.env')
load_dotenv(dotenv_path=dotenv_path)

# --- API Configurations ---
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_BASE_URL = os.getenv("GROQ_API_BASE_URL", "https://api.groq.com/openai/v1")

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_BASE_URL = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")

def _execute_llm_call(provider_name, api_url, headers, payload, timeout):
    """Executes the HTTP POST request and returns JSON response or raises error."""
    response = requests.post(api_url, headers=headers, json=payload, timeout=timeout)
    response.raise_for_status()
    return response.json()

def call_llm(
    prompt: str,
    system_prompt: str = "You are a helpful assistant.",
    primary_groq_model_override: str = None,
    fallback_openrouter_model_override: str = None
) -> str:
    """
    Sends a prompt to Groq API first. If it fails, falls back to OpenRouter.
    """
    default_groq_model = os.getenv("PRIMARY_GROQ_MODEL", "llama3-8b-8192")
    default_openrouter_model = os.getenv("FALLBACK_OPENROUTER_MODEL", "mistralai/mistral-7b-instruct")
    
    groq_model = primary_groq_model_override or default_groq_model
    openrouter_model = fallback_openrouter_model_override or default_openrouter_model
    
    temperature = float(os.getenv("LLM_TEMPERATURE", 0.5))
    messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": prompt}]
    max_retries = int(os.getenv("LLM_MAX_RETRIES", 2))
    backoff_time = float(os.getenv("LLM_BASE_BACKOFF_SECONDS", 1.0))

    # --- Attempt 1: Groq ---
    if GROQ_API_KEY and groq_model:
        headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
        payload = {"model": groq_model, "messages": messages, "temperature": temperature}
        api_url = f"{GROQ_BASE_URL.rstrip('/')}/chat/completions"
        timeout = int(os.getenv("GROQ_TIMEOUT_SECONDS", 15))

        for attempt in range(max_retries):
            try:
                data = _execute_llm_call("Groq", api_url, headers, payload, timeout)
                return data["choices"][0]["message"]["content"].strip()
            except requests.exceptions.RequestException as e:
                print(f"\nDEBUG: [Groq] Error on attempt {attempt + 1}: {e}")
                if attempt < max_retries - 1:
                    time.sleep(backoff_time * (2 ** attempt))
                else:
                    break # Failed all retries

    # --- Attempt 2: OpenRouter Fallback ---
    if OPENROUTER_API_KEY and openrouter_model:
        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": os.getenv("HTTP_REFERER", "http://localhost:3000"),
            "X-Title": os.getenv("X_TITLE", "BittyScout")
        }
        payload = {"model": openrouter_model, "messages": messages, "temperature": temperature}
        api_url = f"{OPENROUTER_BASE_URL.rstrip('/')}/chat/completions"
        timeout = int(os.getenv("OPENROUTER_TIMEOUT_SECONDS", 30))
        try:
            data = _execute_llm_call("OpenRouter", api_url, headers, payload, timeout)
            return data["choices"][0]["message"]["content"].strip()
        except requests.exceptions.RequestException as e:
            print(f"\nDEBUG: [OpenRouter] Fallback failed: {e}")

    return "Error: All LLM providers failed."

def list_available_models():
    """Fetches and lists available models from OpenRouter."""
    if not OPENROUTER_API_KEY:
        print("❌ OPENROUTER_API_KEY not set. Cannot fetch models.")
        return
    try:
        response = requests.get(f"{OPENROUTER_BASE_URL.rstrip('/')}/models")
        response.raise_for_status()
        models = response.json().get('data', [])
        print("--- Available OpenRouter Models ---")
        for model in sorted(models, key=lambda x: x.get('id')):
            print(f"- {model.get('id')}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to fetch models from OpenRouter: {e}")

def set_model(model_name: str):
    """A helper to conceptually set a model, though our main function handles overrides."""
    print(f"ℹ️ Note: `set_model` is a conceptual helper. Use overrides in `call_llm`.")
    pass

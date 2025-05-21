# utils/llm_utils.py

import os
import openai
from dotenv import load_dotenv

load_dotenv()

# Load from .env
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_BASE_URL = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "mistralai/mistral-7b-instruct")

# Setup OpenAI client to route through OpenRouter
openai.api_key = OPENROUTER_API_KEY
openai.api_base = OPENROUTER_BASE_URL

def call_llm(prompt: str, system_prompt: str = "") -> str:
    response = openai.ChatCompletion.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7
    )
    return response.choices[0].message.content.strip()

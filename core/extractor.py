# core/extractor.py
"""
Metadata extraction from research-paper text using a cloud LLM.

Two providers are supported, selected with the LLM_PROVIDER env var:

  LLM_PROVIDER=gemini      (default) Google AI Studio free tier.
                           Needs GOOGLE_API_KEY in .env — get one free at
                           https://aistudio.google.com/apikey
  LLM_PROVIDER=huggingface  Hugging Face Inference Providers (paid credits).
                           Needs HF_TOKEN in .env.

Both paths return {"title": str, "authors": [str]}.
"""

import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "gemini").lower()

# --- Hugging Face (Inference Providers) ---
HF_TOKEN = os.getenv("HF_TOKEN")
HF_MODEL = os.getenv("HF_MODEL", "meta-llama/Llama-3.1-8B-Instruct")
HF_API_URL = "https://router.huggingface.co/v1/chat/completions"

# --- Google Gemini (AI Studio free tier) ---
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")


def _extract_huggingface(text: str) -> dict:
    """Extract via HF Inference Providers chat API (OpenAI-compatible)."""
    if not HF_TOKEN:
        return {"title": "Extraction Failed", "authors": ["HF_TOKEN is not set in .env"]}

    text_chunk = text[:6000]
    headers = {"Authorization": f"Bearer {HF_TOKEN}", "Content-Type": "application/json"}
    payload = {
        "model": HF_MODEL,
        "messages": [
            {
                "role": "system",
                "content": (
                    "You extract metadata from research papers. Respond with ONLY "
                    'a JSON object with exactly two keys: "title" (a string) and '
                    '"authors" (an array of author name strings). No other text.'
                ),
            },
            {
                "role": "user",
                "content": (
                    "Extract the title and the list of all author names from the "
                    f"following research paper text:\n---\n{text_chunk}\n---"
                ),
            },
        ],
        "response_format": {"type": "json_object"},
        "max_tokens": 512,
        "temperature": 0,
    }

    print(f"Querying Hugging Face Inference Providers with {HF_MODEL}...")
    try:
        response = requests.post(HF_API_URL, headers=headers, json=payload, timeout=120)
        response.raise_for_status()
        response_data = response.json()
        content = (
            response_data.get("choices", [{}])[0].get("message", {}).get("content", "")
        )
        if not content:
            raise ValueError(f"API returned no message content: {response_data}")
        data = json.loads(content)
        return {
            "title": data.get("title", "Title not in JSON"),
            "authors": data.get("authors", []),
        }
    except Exception as e:
        print(f"CRITICAL: Metadata extraction failed. Error: {e}")
        return {"title": "Extraction Failed", "authors": [f"An error occurred: {e}"]}


def _extract_gemini(text: str) -> dict:
    """Extract via Google AI Studio (Gemini) free tier."""
    if not GOOGLE_API_KEY:
        return {
            "title": "Extraction Failed",
            "authors": ["GOOGLE_API_KEY is not set in .env — get one free at https://aistudio.google.com/apikey"],
        }

    text_chunk = text[:12000]
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent"
    prompt = (
        "Extract the title and the list of all author names from the following "
        "research paper text. If the document is not a research paper, return the "
        'document\'s own heading as "title" and an empty "authors" list.\n'
        f"---\n{text_chunk}\n---"
    )
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "responseMimeType": "application/json",
            "temperature": 0,
            "maxOutputTokens": 512,
        },
    }

    print(f"Querying Google AI Studio with {GEMINI_MODEL}...")
    try:
        response = requests.post(url, params={"key": GOOGLE_API_KEY}, json=payload, timeout=120)
        response.raise_for_status()
        response_data = response.json()
        content = (
            response_data.get("candidates", [{}])[0]
            .get("content", {})
            .get("parts", [{}])[0]
            .get("text", "")
        )
        if not content:
            raise ValueError(f"API returned no content: {response_data}")
        data = json.loads(content)
        return {
            "title": data.get("title", "Title not in JSON"),
            "authors": data.get("authors", []),
        }
    except Exception as e:
        print(f"CRITICAL: Metadata extraction failed. Error: {e}")
        return {"title": "Extraction Failed", "authors": [f"An error occurred: {e}"]}


def extract_metadata_from_text(text: str) -> dict:
    """Extract {"title", "authors"} using the configured LLM provider."""
    if LLM_PROVIDER == "huggingface":
        return _extract_huggingface(text)
    return _extract_gemini(text)

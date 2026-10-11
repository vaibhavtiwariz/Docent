# core/extractor.py

import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()
HF_TOKEN = os.getenv("HF_TOKEN")
# Instruction-tuned model via Hugging Face Inference Providers (OpenAI-compatible).
# Override with HF_MODEL env var, e.g. "Qwen/Qwen2.5-7B-Instruct".
HF_MODEL = os.getenv("HF_MODEL", "meta-llama/Llama-3.1-8B-Instruct")
API_URL = "https://router.huggingface.co/v1/chat/completions"

headers = {
    "Authorization": f"Bearer {HF_TOKEN}",
    "Content-Type": "application/json",
}


def extract_metadata_from_text(text: str) -> dict:
    """
    Calls the Hugging Face Inference Providers chat API with an
    instruction-tuned LLM and returns {"title": str, "authors": [str]}.
    """
    if not HF_TOKEN:
        return {"title": "Extraction Failed", "authors": ["HF_TOKEN is not set in .env"]}

    text_chunk = text[:6000]

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
        response = requests.post(API_URL, headers=headers, json=payload, timeout=120)
        response.raise_for_status()

        response_data = response.json()
        content = (
            response_data.get("choices", [{}])[0]
            .get("message", {})
            .get("content", "")
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

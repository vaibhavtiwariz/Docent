# core/extractor.py

import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()
HF_TOKEN = os.getenv("HF_TOKEN")

# --- Switched to a known working model endpoint ---
API_URL = "https://api-inference.huggingface.co/models/gpt2"
headers = {"Authorization": f"Bearer {HF_TOKEN}"}

def extract_metadata_from_text(text: str) -> dict:
    """
    Calls the Hugging Face Inference API using the GPT-2 model endpoint.
    """
    text_chunk = text[:3000]

    # --- Prompt format for the GPT-2 model ---
    prompt = f"""
    Extract the title and a list of all author names from the following research paper text.
    Provide the output strictly in the format of a single JSON object with two keys: "title" and "authors".

    Text:
    ---
    {text_chunk}
    ---

    JSON Output:
    """

    payload = {
        "inputs": prompt,
        "parameters": { "max_new_tokens": 512 }
    }

    print("Querying the Hugging Face Inference API with GPT-2...")
    try:
        response = requests.post(API_URL, headers=headers, json=payload, timeout=120)
        response.raise_for_status() 

        response_data = response.json()
        print(f"RAW API RESPONSE: {response_data}")

        if isinstance(response_data, list) and len(response_data) > 0 and 'generated_text' in response_data[0]:
            generated_text = response_data[0]['generated_text']
        else:
            raise ValueError(f"API returned an unexpected response format: {response_data}")

        json_start = generated_text.find('{')
        json_end = generated_text.rfind('}') + 1

        if json_start != -1 and json_end != -1:
            json_str = generated_text[json_start:json_end]
            if not json_str:
                raise ValueError("Extracted JSON string is empty.")
            data = json.loads(json_str)
            return {
                "title": data.get("title", "Title not in JSON"),
                "authors": data.get("authors", [])
            }
        else:
            raise ValueError("No JSON object found in the model's output string.")

    except Exception as e:
        print(f"CRITICAL: Metadata extraction failed. Error: {e}")
        return {"title": "Extraction Failed", "authors": [f"An error occurred: {e}"]}

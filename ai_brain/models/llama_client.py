import requests
import os
from pprint import pprint

URL = "http://localhost:11434/api/generate"

def ask_llama(prompt, model="tinyllama", max_tokens=250):
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {
            "num_predict": max_tokens,
            "temperature": 0.6
        }
    }

    try:
        r = requests.post(URL, json=payload, timeout=60)
        r.raise_for_status()
        data = r.json()
        return data.get("response", "").strip()
    except Exception as e:
        print(f"Error calling local LLM ({model}): {e}")
        return "WAIT 0"

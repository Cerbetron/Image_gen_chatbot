import requests
from .config import OLLAMA_URL, OLLAMA_MODEL


def chat(message: str) -> str:
    payload = {
        "model": OLLAMA_MODEL,
        "messages": [
            {"role": "system", "content": "You are a friendly assistant helping users with their Food Score queries."},
            {"role": "user", "content": message},
        ],
    }
    try:
        r = requests.post(OLLAMA_URL, json=payload, timeout=20)
        return r.json().get("message", {}).get("content", "")
    except Exception:
        return "Sorry, I couldn't reach the language model."

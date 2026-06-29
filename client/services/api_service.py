import requests
from config import URL_BACKEND

def send_for_translation(text: str) -> dict:
    payload = {"text": text}
    response = requests.post(URL_BACKEND, json=payload, timeout=180)
    
    if response.status_code == 200:
        return response.json()
    else:
        raise RuntimeError(f"Server error: HTTP {response.status_code}")
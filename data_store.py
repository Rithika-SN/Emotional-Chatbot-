# data_store.py
# Simple JSON-based storage for mood history

import json
from datetime import datetime
from pathlib import Path

DEFAULT_PATH = Path("user_data.json")

def load_data(path=DEFAULT_PATH):
    if not path.exists():
        return {"records": []}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_data(data, path=DEFAULT_PATH):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def add_message_record(user_id: str, text: str, emotion: str, tone: str, sentiment: float, path=DEFAULT_PATH):
    data = load_data(path)
    record = {
        "user_id": user_id,
        "timestamp": datetime.utcnow().isoformat(),
        "text": text,
        "emotion": emotion,
        "tone": tone,
        "sentiment": sentiment
    }
    data.setdefault("records", []).append(record)
    save_data(data, path)
    return record

def get_today_messages(user_id: str, path=DEFAULT_PATH):
    data = load_data(path)
    today = []
    # naive UTC date check
    from datetime import datetime
    for r in data.get("records", []):
        if r["user_id"] == user_id:
            today.append(r)
    return today

def get_all_messages(user_id: str, path=DEFAULT_PATH):
    data = load_data(path)
    return [r for r in data.get("records", []) if r["user_id"] == user_id]

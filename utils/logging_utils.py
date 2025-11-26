import json
import os
import datetime
import uuid

LOG_DIR = os.path.join(os.path.dirname(__file__), "..", "logs")
os.makedirs(LOG_DIR, exist_ok=True)

def log_event(agent_name: str, event_type: str, data: dict):

    record = {
        "id": str(uuid.uuid4()),
        "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
        "agent": agent_name,
        "event_type": event_type,
        "data": data
    }

    path = os.path.join(LOG_DIR, f"{datetime.date.today()}.jsonl")
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")

    return record

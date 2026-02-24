import json
from pathlib import Path

REQ = Path("history_request.json")
RESP = Path("history_response.json")

def send(obj):
    if RESP.exists():
        RESP.unlink()
    REQ.write_text(json.dumps(obj, indent=2), encoding="utf-8")
    print("Wrote history_request.json")

if __name__ == "__main__":
    send({
        "action": "getSummary",
        "startTime": "2026-02-01T00:00:00Z",
        "endTime": "2026-12-31T23:59:59Z",
        "groupBy": "eventType"
    })
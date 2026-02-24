import json, os, time
from pathlib import Path
from datetime import datetime, timezone

REQ = Path("history_request.json")
RESP = Path("history_response.json")

def write_req(obj):
    if RESP.exists():
        RESP.unlink()
    REQ.write_text(json.dumps(obj, indent=2), encoding="utf-8")

def wait_resp(timeout=5.0):
    start = time.time()
    while time.time() - start < timeout:
        if RESP.exists():
            return json.loads(RESP.read_text(encoding="utf-8"))
        time.sleep(0.05)
    raise TimeoutError("Timed out waiting for history_response.json")

def iso_now():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

if __name__ == "__main__":
    # 1) logEvent
    t1 = iso_now()
    write_req({
        "action": "logEvent",
        "timestamp": t1,
        "source": "demo_client",
        "eventType": "purchase",
        "payload": { "category": "Food", "amount": 12.50 }
    })
    print("logEvent response:", wait_resp())

    # 2) logEvent
    t2 = iso_now()
    write_req({
        "action": "logEvent",
        "timestamp": t2,
        "source": "demo_client",
        "eventType": "purchase",
        "payload": { "category": "Games", "amount": 59.99 }
    })
    print("logEvent response:", wait_resp())

    # 3) getSummary
    write_req({
        "action": "getSummary",
        "startTime": "2026-02-01T00:00:00Z",
        "endTime": "2026-12-31T23:59:59Z",
        "groupBy": "eventType"
    })
    print("getSummary response:", wait_resp())

    # 4) getTopN
    write_req({
        "action": "getTopN",
        "startTime": "2026-02-01T00:00:00Z",
        "endTime": "2026-12-31T23:59:59Z",
        "field": "payload.category",
        "n": 3
    })
    print("getTopN response:", wait_resp())
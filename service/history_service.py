from __future__ import annotations
import json
import os
import time
from pathlib import Path
from typing import Any, Dict

from config import ServiceConfig
from protocol import ok, err
from storage import append_event, read_events, ensure_storage
from analytics import summarize, top_n, parse_iso8601

CFG = ServiceConfig()

def atomic_write_json(path: Path, data: Dict[str, Any]) -> None:
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    tmp.replace(path)

def try_acquire_lock(lock_path: Path) -> bool:
    # Exclusive create
    try:
        fd = os.open(str(lock_path), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        os.close(fd)
        return True
    except FileExistsError:
        return False

def release_lock(lock_path: Path) -> None:
    try:
        lock_path.unlink(missing_ok=True)
    except Exception:
        pass

def load_request(req_path: Path) -> Dict[str, Any]:
    raw = req_path.read_text(encoding="utf-8")
    return json.loads(raw)

def validate_common(req: Dict[str, Any]) -> str:
    action = req.get("action")
    if action not in ("logEvent", "getSummary", "getTopN"):
        raise ValueError("Missing/invalid 'action'. Must be one of: logEvent, getSummary, getTopN.")
    return action

def handle_log_event(req: Dict[str, Any]) -> Dict[str, Any]:
    timestamp = req.get("timestamp")
    source = req.get("source")
    event_type = req.get("eventType")
    payload = req.get("payload", {})

    if not isinstance(timestamp, str):
        return err("logEvent requires 'timestamp' as a string.")
    if not isinstance(source, str) or not source:
        return err("logEvent requires 'source' as a non-empty string.")
    if not isinstance(event_type, str) or not event_type:
        return err("logEvent requires 'eventType' as a non-empty string.")
    if payload is not None and not isinstance(payload, dict):
        return err("logEvent optional 'payload' must be an object (JSON dict).")

    # validate timestamp parse
    try:
        parse_iso8601(timestamp)
    except ValueError as e:
        return err(str(e))

    event = {
        "timestamp": timestamp,
        "source": source,
        "eventType": event_type,
        "payload": payload if isinstance(payload, dict) else {}
    }

    append_event(CFG.log_file, event)
    return ok()

def validate_time_range(req: Dict[str, Any], action_name: str) -> tuple[str, str]:
    start = req.get("startTime")
    end = req.get("endTime")

    if not isinstance(start, str) or not isinstance(end, str):
        raise ValueError(f"{action_name} requires 'startTime' and 'endTime' as strings.")

    parse_iso8601(start)
    parse_iso8601(end)
    return start, end


def load_all_events() -> list[Dict[str, Any]]:
    return list(read_events(CFG.log_file))

def handle_get_summary(req: Dict[str, Any]) -> Dict[str, Any]:
    group_by = req.get("groupBy")

    if not isinstance(group_by, str) or not group_by:
        return err("getSummary requires 'groupBy' as a non-empty string.")

    try:
        start, end = validate_time_range(req, "getSummary")
    except ValueError as e:
        return err(str(e))

    events = load_all_events()
    result = summarize(events, start, end, group_by)
    return ok(result)

    events = list(read_events(CFG.log_file))
    result = summarize(events, start, end, group_by)
    return ok(result)

def handle_get_topn(req: Dict[str, Any]) -> Dict[str, Any]:
    field = req.get("field")
    n = req.get("n")

    if not isinstance(field, str) or not field:
        return err("getTopN requires 'field' as a non-empty string.")
    if not isinstance(n, int) or n < 0:
        return err("getTopN requires 'n' as a non-negative integer.")

    try:
        start, end = validate_time_range(req, "getTopN")
    except ValueError as e:
        return err(str(e))

    events = load_all_events()
    result = top_n(events, start, end, field, n)
    return ok(result)

def process_once() -> None:
    req_path = Path(CFG.request_file)
    resp_path = Path(CFG.response_file)
    lock_path = Path(CFG.lock_file)

    if not req_path.exists():
        return
    # If response already exists, wait for consumer to delete it.
    if resp_path.exists():
        return
    if not try_acquire_lock(lock_path):
        return

    try:
        try:
            req = load_request(req_path)
        except json.JSONDecodeError:
            atomic_write_json(resp_path, err("Invalid JSON in history_request.json"))
            return
        except Exception as e:
            atomic_write_json(resp_path, err(f"Failed reading request: {e}"))
            return

        try:
            action = validate_common(req)
        except ValueError as e:
            atomic_write_json(resp_path, err(str(e)))
            return

        if action == "logEvent":
            out = handle_log_event(req)
        elif action == "getSummary":
            out = handle_get_summary(req)
        else:
            out = handle_get_topn(req)

        atomic_write_json(resp_path, out)

        # Consumer should delete request after receiving response; we also delete request to prevent replays.
        try:
            req_path.unlink(missing_ok=True)
        except Exception:
            pass
    finally:
        release_lock(lock_path)

def main() -> None:
    ensure_storage(CFG.log_file)
    print("History / Analytics Tracker microservice running.")
    print(f"Watching for: {CFG.request_file}")
    print(f"Writing response: {CFG.response_file}")
    print(f"Persistent log: {CFG.log_file}")

    while True:
        process_once()
        time.sleep(CFG.poll_interval_seconds)

if __name__ == "__main__":
    main()
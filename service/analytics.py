from __future__ import annotations
from typing import Any, Dict, List, Tuple
from datetime import datetime, timezone

def parse_iso8601(ts: str) -> datetime:
    """
    Accepts:
    - 2026-02-23T00:10:00Z
    - 2026-02-23T00:10:00+00:00
    - 2026-02-23T00:10:00  (treated as UTC)
    """
    s = ts.strip()
    if s.endswith("Z"):
        s = s[:-1] + "+00:00"
    try:
        dt = datetime.fromisoformat(s)
    except ValueError:
        raise ValueError(f"Invalid ISO timestamp: {ts}")
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)

def in_range(event_ts: str, start: str, end: str) -> bool:
    t = parse_iso8601(event_ts)
    s = parse_iso8601(start)
    e = parse_iso8601(end)
    return s <= t <= e

def get_field(event: Dict[str, Any], field_path: str) -> Any:
    """
    Supports dot paths like:
    - "eventType"
    - "payload.category"
    """
    parts = field_path.split(".")
    cur: Any = event
    for p in parts:
        if isinstance(cur, dict) and p in cur:
            cur = cur[p]
        else:
            return None
    return cur

def summarize(events: List[Dict[str, Any]], start: str, end: str, group_by: str) -> Dict[str, Any]:
    totals: Dict[str, int] = {}
    count = 0

    for ev in events:
        ts = ev.get("timestamp")
        if not isinstance(ts, str):
            continue
        if not in_range(ts, start, end):
            continue

        val = get_field(ev, group_by)
        if val is None:
            continue
        key = str(val)
        totals[key] = totals.get(key, 0) + 1
        count += 1

    return {
        "range": {"startTime": start, "endTime": end},
        "groupBy": group_by,
        "totals": totals,
        "count": count
    }

def top_n(events: List[Dict[str, Any]], start: str, end: str, field: str, n: int) -> Dict[str, Any]:
    counts: Dict[str, int] = {}

    for ev in events:
        ts = ev.get("timestamp")
        if not isinstance(ts, str):
            continue
        if not in_range(ts, start, end):
            continue

        val = get_field(ev, field)
        if val is None:
            continue
        key = str(val)
        counts[key] = counts.get(key, 0) + 1

    # sort: count desc, then value asc
    ordered: List[Tuple[str, int]] = sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))
    top = [{"value": k, "count": c} for k, c in ordered[: max(0, n)]]

    return {
        "range": {"startTime": start, "endTime": end},
        "field": field,
        "top": top
    }
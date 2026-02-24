from __future__ import annotations
import json
from pathlib import Path
from typing import Dict, Any, Iterable, List

def ensure_storage(log_path: Path) -> None:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    if not log_path.exists():
        log_path.write_text("", encoding="utf-8")

def append_event(log_path: Path, event: Dict[str, Any]) -> None:
    ensure_storage(log_path)
    with log_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(event, ensure_ascii=False) + "\n")

def read_events(log_path: Path) -> Iterable[Dict[str, Any]]:
    ensure_storage(log_path)
    with log_path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                yield json.loads(line)
            except json.JSONDecodeError:
                # skip corrupt line instead of crashing
                continue
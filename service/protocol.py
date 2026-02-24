from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict, Optional, Literal

Action = Literal["logEvent", "getSummary", "getTopN"]

@dataclass
class ServiceError(Exception):
    message: str

def ok(payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    base = {"status": "ok"}
    if payload:
        base.update(payload)
    return base

def err(message: str) -> Dict[str, Any]:
    return {"status": "error", "message": message}
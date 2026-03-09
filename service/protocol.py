from __future__ import annotations
from typing import Any, Dict, Optional


def ok(payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    base = {"status": "ok"}
    if payload:
        base.update(payload)
    return base


def err(message: str) -> Dict[str, Any]:
    return {"status": "error", "message": message}
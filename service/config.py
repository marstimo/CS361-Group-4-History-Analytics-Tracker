from dataclasses import dataclass
from pathlib import Path

@dataclass(frozen=True)
class ServiceConfig:
    request_file: str = "history_request.json"
    response_file: str = "history_response.json"
    lock_file: str = "history_request.lock"

    data_dir: Path = Path("data")
    log_file: Path = Path("data/history_log.jsonl")

    poll_interval_seconds: float = 0.10
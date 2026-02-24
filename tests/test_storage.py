from pathlib import Path
import tempfile
from service.storage import append_event, read_events, ensure_storage

def test_append_and_read():
    with tempfile.TemporaryDirectory() as d:
        log = Path(d) / "history_log.jsonl"
        ensure_storage(log)
        append_event(log, {"timestamp":"2026-02-10T00:00:00Z","eventType":"x"})
        append_event(log, {"timestamp":"2026-02-10T00:00:01Z","eventType":"y"})
        evs = list(read_events(log))
        assert len(evs) == 2
        assert evs[0]["eventType"] == "x"
        assert evs[1]["eventType"] == "y"
from service.analytics import top_n, summarize

def test_topn_tie_break_alpha():
    events = [
        {"timestamp":"2026-02-10T00:00:00Z","eventType":"x","payload":{"category":"B"}},
        {"timestamp":"2026-02-10T00:00:01Z","eventType":"x","payload":{"category":"A"}},
    ]
    out = top_n(events, "2026-02-01T00:00:00Z", "2026-02-28T23:59:59Z", "payload.category", 10)
    # counts tie 1-1, sorted A then B
    assert out["top"][0]["value"] == "A"
    assert out["top"][1]["value"] == "B"

def test_summary_group_eventType():
    events = [
        {"timestamp":"2026-02-10T00:00:00Z","eventType":"purchase"},
        {"timestamp":"2026-02-10T00:00:01Z","eventType":"refund"},
        {"timestamp":"2026-02-10T00:00:02Z","eventType":"purchase"},
    ]
    out = summarize(events, "2026-02-01T00:00:00Z", "2026-02-28T23:59:59Z", "eventType")
    assert out["totals"]["purchase"] == 2
    assert out["totals"]["refund"] == 1
    assert out["count"] == 3
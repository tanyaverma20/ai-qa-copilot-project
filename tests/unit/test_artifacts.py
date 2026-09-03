from __future__ import annotations

import json

from qa_copilot.artifacts import load_failure_artifacts


def test_load_failure_artifacts_skips_malformed_json(tmp_path):
    good_artifact = {
        "nodeid": "tests/api/test_orders_api.py::test_create_order",
        "failed_at": "2026-07-02T10:00:00+00:00",
        "phase": "call",
        "duration_seconds": 0.2,
        "longrepr": "AssertionError: expected 201 but got 500",
        "keywords": ["api"],
    }
    (tmp_path / "good.json").write_text(
        json.dumps(good_artifact),
        encoding="utf-8",
    )
    (tmp_path / "broken.json").write_text("{not-valid-json", encoding="utf-8")

    artifacts = load_failure_artifacts(tmp_path)

    assert len(artifacts) == 1
    assert artifacts[0].nodeid == "tests/api/test_orders_api.py::test_create_order"

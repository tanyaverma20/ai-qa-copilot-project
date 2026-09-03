from __future__ import annotations

from qa_copilot.artifacts import FailureArtifact
from qa_copilot.prompt_builder import build_diagnosis_prompt


def test_build_diagnosis_prompt_contains_failure_context():
    artifact = FailureArtifact(
        nodeid="tests/api/test_orders_api.py::test_create_order_rejects_insufficient_stock",
        failed_at="2026-07-02T10:00:00+00:00",
        phase="call",
        duration_seconds=0.13,
        longrepr="AssertionError: expected 409 but got 500",
        keywords=["api"],
    )

    prompt = build_diagnosis_prompt([artifact])

    assert "expected 409 but got 500" in prompt
    assert "Suspected root cause" in prompt
    assert "test script bug" in prompt


def test_build_diagnosis_prompt_groups_failure_modes():
    artifacts = [
        FailureArtifact(
            nodeid="tests/api/test_orders_api.py::test_create_order_contract",
            failed_at="2026-07-02T10:02:00+00:00",
            phase="call",
            duration_seconds=0.18,
            longrepr="AssertionError: expected status code 201 but got 422",
            keywords=["api", "api-assertion", "contract"],
        ),
        FailureArtifact(
            nodeid="tests/e2e/test_product_search.py::test_search_filters_results",
            failed_at="2026-07-02T10:03:00+00:00",
            phase="call",
            duration_seconds=3.2,
            longrepr="Flaky test summary: passed 7 times and failed 3 times",
            keywords=["e2e", "playwright", "flaky"],
        ),
        FailureArtifact(
            nodeid="tests/conftest.py::db_seed_fixture",
            failed_at="2026-07-02T10:04:00+00:00",
            phase="setup",
            duration_seconds=0.05,
            longrepr="sqlite3.OperationalError: no such table: products",
            keywords=["fixture", "setup", "database"],
        ),
    ]

    prompt = build_diagnosis_prompt(artifacts)

    assert "- Failure mode matrix" in prompt
    assert "Failure mode groups:" in prompt
    assert "### API contract" in prompt
    assert "### Flaky/timing" in prompt
    assert "### Environment/setup" in prompt
    assert prompt.index("### API contract") < prompt.index(
        "tests/api/test_orders_api.py::test_create_order_contract"
    )
    assert prompt.index("### Flaky/timing") < prompt.index(
        "tests/e2e/test_product_search.py::test_search_filters_results"
    )
    assert prompt.index("### Environment/setup") < prompt.index(
        "tests/conftest.py::db_seed_fixture"
    )


def test_build_diagnosis_prompt_prioritizes_setup_failures():
    artifact = FailureArtifact(
        nodeid="tests/e2e/test_checkout_flow.py::test_setup_before_checkout",
        failed_at="2026-07-02T10:05:00+00:00",
        phase="setup",
        duration_seconds=0.07,
        longrepr="TimeoutError: fixture setup failed before checkout",
        keywords=["api", "contract", "playwright", "flaky", "setup"],
    )

    prompt = build_diagnosis_prompt([artifact])

    assert "### Environment/setup" in prompt
    assert "### Flaky/timing" not in prompt
    assert "### API contract" not in prompt
    assert "### UI/E2E behavior" not in prompt
    assert "### Product/API behavior" not in prompt

from __future__ import annotations

from pathlib import Path

import pytest

from qa_copilot.pr_comment import (
    build_pr_comment,
    extract_section,
    redact_comment_text,
    write_pr_comment,
)

SAMPLE_DIAGNOSIS = "\n".join(
    (
        "# AI Diagnosis Report",
        "",
        "## Summary",
        "",
        "The example artifact set shows API, UI, flaky, and setup failures.",
        "",
        "## Failure Mode Matrix",
        "",
        (
            "| Failure Mode | Affected Test / Artifact | Evidence | "
            "Likely Classification | Next Action |"
        ),
        "| --- | --- | --- | --- | --- |",
        (
            "| Product/API behavior | `tests/api/test_orders_api.py::test_create_order` | "
            "Expected `409`, received `500` | Product bug | "
            "Map stock errors to HTTP `409`. |"
        ),
        (
            "| API contract | `tests/api/test_orders_api.py::test_create_order_contract` | "
            "`quantity` is missing | Contract drift | Compare schema and request body. |"
        ),
        (
            "| Flaky/timing | `tests/e2e/test_product_search.py::test_search_filters_results` | "
            "7 pass / 3 fail | Flaky test | Wait on stable app state. |"
        ),
        "",
        "## Suggested fix",
        "",
        "- Map domain errors to explicit API responses.",
        "- Keep API tests aligned with the public request/response schema.",
        "- Make flaky UI assertions wait on stable app state.",
    )
)


def test_extract_section_returns_named_markdown_section():
    summary = extract_section(SAMPLE_DIAGNOSIS, "Summary")

    assert "example artifact set" in summary
    assert "Failure Mode Matrix" not in summary


def test_extract_section_returns_empty_string_for_missing_section():
    assert extract_section(SAMPLE_DIAGNOSIS, "Not Here") == ""


def test_build_pr_comment_includes_core_sections():
    comment = build_pr_comment(SAMPLE_DIAGNOSIS)

    assert "## AI QA Copilot Diagnosis Preview" in comment
    assert "Dry-run PR comment preview" in comment
    assert "### Summary" in comment
    assert "### Failure Mode Matrix" in comment
    assert "### Recommended next steps" in comment
    assert "### Artifacts" in comment
    assert "### Safety" in comment


def test_build_pr_comment_includes_failure_mode_matrix_summary():
    comment = build_pr_comment(SAMPLE_DIAGNOSIS)

    assert "Product/API behavior" in comment
    assert "API contract" in comment
    assert "Flaky/timing" in comment
    assert "tests/api/test_orders_api.py::test_create_order" in comment


def test_build_pr_comment_handles_report_without_matrix():
    comment = build_pr_comment("# AI Diagnosis Report\n\n## Summary\n\nNo failures.")

    assert "No failures." in comment
    assert "No failure mode matrix was found" in comment


@pytest.mark.parametrize(
    ("raw", "secret"),
    (
        ("token sk-test-secret-value", "sk-test-secret-value"),
        ("Authorization: Bearer abc.def-123", "Bearer abc.def-123"),
        ("api_key = deepseek-secret", "deepseek-secret"),
        ("password: super-secret", "super-secret"),
        ("cookie=session-id", "session-id"),
    ),
)
def test_redact_comment_text_removes_secret_like_values(raw: str, secret: str):
    redacted = redact_comment_text(raw)

    assert secret not in redacted
    assert "[REDACTED]" in redacted


def test_build_pr_comment_redacts_secret_like_values():
    diagnosis = """
## Summary

Failure with key sk-test-secret and Authorization: Bearer abc.def
"""

    comment = build_pr_comment(diagnosis)

    assert "sk-test-secret" not in comment
    assert "Bearer abc.def" not in comment
    assert "[REDACTED]" in comment


def test_build_pr_comment_redacts_provider_config_like_values():
    diagnosis = """
## Summary

Provider details used DEEPSEEK_API_KEY and https://tenant.internal.example/v1.
"""

    comment = build_pr_comment(diagnosis)

    assert "DEEPSEEK_API_KEY" not in comment
    assert "tenant.internal.example" not in comment
    assert "[REDACTED]" in comment


def test_write_pr_comment_writes_markdown(tmp_path: Path):
    input_path = tmp_path / "diagnosis.md"
    output_path = tmp_path / "comment.md"
    input_path.write_text(SAMPLE_DIAGNOSIS, encoding="utf-8")

    write_pr_comment(input_path, output_path)

    text = output_path.read_text(encoding="utf-8")
    assert "AI QA Copilot Diagnosis Preview" in text
    assert "Failure Mode Matrix" in text

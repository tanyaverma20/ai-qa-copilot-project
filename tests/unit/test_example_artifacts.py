from __future__ import annotations

from pathlib import Path

from qa_copilot.artifacts import load_failure_artifacts
from qa_copilot.prompt_builder import build_diagnosis_prompt

EXAMPLES = Path("reports/examples")
CATALOG = Path("docs/diagnosis-examples.md")

EXPECTED_EXAMPLE_FILES = {
    "api-contract-failure.json",
    "fixture-setup-failure.json",
    "flaky-search-failure.json",
    "playwright-visibility-failure.json",
    "sample-failure.json",
}
SECRET_PATTERNS = (
    "sk-",
    "authorization",
    "bearer ",
    "api_key",
    "password",
    "cookie",
)


def test_example_artifact_file_set_is_intentional():
    json_files = {path.name for path in EXAMPLES.glob("*.json")}

    assert json_files == EXPECTED_EXAMPLE_FILES


def test_all_example_json_files_are_loaded():
    artifacts = load_failure_artifacts(EXAMPLES)

    assert len(artifacts) == len(EXPECTED_EXAMPLE_FILES)


def test_example_artifacts_do_not_contain_secret_patterns():
    for path in EXAMPLES.glob("*.json"):
        text = path.read_text(encoding="utf-8").lower()

        for pattern in SECRET_PATTERNS:
            assert pattern not in text, f"{path} contains secret-like pattern {pattern!r}"


def test_example_docs_reference_every_artifact_file():
    catalog = CATALOG.read_text(encoding="utf-8")
    sample_report = (EXAMPLES / "sample-ai-diagnosis.md").read_text(encoding="utf-8")

    for filename in EXPECTED_EXAMPLE_FILES:
        assert filename in catalog
        assert filename in sample_report


def test_sample_diagnosis_report_has_failure_mode_matrix():
    sample_report = (EXAMPLES / "sample-ai-diagnosis.md").read_text(encoding="utf-8")

    assert "## Failure Mode Matrix" in sample_report
    assert (
        "| Failure Mode | Affected Test / Artifact | Evidence | "
        "Likely Classification | Next Action |"
    ) in sample_report
    assert (
        "`tests/api/test_orders_api.py::test_create_order_rejects_insufficient_stock` / "
        "`sample-failure.json`"
    ) in sample_report
    assert "Expected `409`, received `500`" in sample_report
    assert "Product/API behavior" in sample_report
    assert "API contract" in sample_report
    assert "UI/E2E behavior" in sample_report
    assert "Flaky/timing" in sample_report
    assert "Environment/setup" in sample_report


def test_example_artifacts_cover_core_qa_failure_modes():
    artifacts = load_failure_artifacts(EXAMPLES)
    keywords = {keyword for artifact in artifacts for keyword in artifact.keywords}

    assert "playwright" in keywords
    assert "api-assertion" in keywords
    assert "flaky" in keywords
    assert "fixture" in keywords
    assert "setup" in keywords


def test_example_artifacts_build_rich_diagnosis_prompt():
    artifacts = load_failure_artifacts(EXAMPLES)

    prompt = build_diagnosis_prompt(artifacts)

    assert "tests/e2e/test_checkout_flow.py::test_checkout_button_enables_payment" in prompt
    assert "expect(locator).to_be_visible()" in prompt
    assert "tests/api/test_orders_api.py::test_create_order_contract" in prompt
    assert "expected status code 201 but got 422" in prompt
    assert "tests/e2e/test_product_search.py::test_search_filters_results" in prompt
    assert "passed 7 times and failed 3 times" in prompt
    assert "tests/conftest.py::db_seed_fixture" in prompt
    assert "sqlite3.OperationalError" in prompt


def test_example_artifacts_prompt_groups_demo_failure_modes():
    artifacts = load_failure_artifacts(EXAMPLES)

    prompt = build_diagnosis_prompt(artifacts)

    assert "Failure mode groups:" in prompt
    assert "### Product/API behavior" in prompt
    assert "### API contract" in prompt
    assert "### UI/E2E behavior" in prompt
    assert "### Flaky/timing" in prompt
    assert "### Environment/setup" in prompt

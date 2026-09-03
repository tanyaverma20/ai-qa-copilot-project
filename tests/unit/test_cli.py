from __future__ import annotations

import json

import pytest

from qa_copilot.cli import generate_report
from qa_copilot.cli import main as cli_main
from tests.helpers import clear_provider_env


def test_generate_report_writes_no_artifacts_message(tmp_path):
    output = tmp_path / "diagnosis.md"

    generate_report(tmp_path / "missing", output)

    assert "No failure artifacts were found." in output.read_text(encoding="utf-8")


def test_generate_report_writes_diagnosis_for_failure_artifact(tmp_path, monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    failures = tmp_path / "failures"
    failures.mkdir()
    (failures / "failure.json").write_text(
        json.dumps(
            {
                "nodeid": "tests/api/test_orders_api.py::test_create_order",
                "failed_at": "2026-07-02T10:00:00+00:00",
                "phase": "call",
                "duration_seconds": 0.12,
                "longrepr": "AssertionError: expected 409 but got 500",
                "keywords": ["api", "orders"],
            }
        ),
        encoding="utf-8",
    )
    output = tmp_path / "diagnosis.md"

    generate_report(failures, output)

    report = output.read_text(encoding="utf-8")
    assert "# AI Diagnosis Report" in report
    assert "API key is not configured" in report


def test_cli_lists_supported_providers(monkeypatch, capsys):
    monkeypatch.setattr("sys.argv", ["qa-copilot", "--list-providers"])

    cli_main()

    output = json.loads(capsys.readouterr().out)
    assert output["deepseek"]["api_style"] == "chat"
    assert output["openai"]["api_style"] == "responses"


def test_cli_checks_provider_configuration(monkeypatch, capsys):
    clear_provider_env(monkeypatch)
    monkeypatch.setattr("sys.argv", ["qa-copilot", "--check-provider"])
    monkeypatch.setenv("AI_PROVIDER", "deepseek")
    monkeypatch.setenv("DEEPSEEK_API_KEY", "secret-deepseek-key")

    cli_main()

    output = json.loads(capsys.readouterr().out)
    assert output["ok"] is True
    assert output["provider"] == "deepseek"
    assert output["model"] == "deepseek-chat"
    assert output["base_url"] == "https://api.deepseek.com"
    assert output["api_key_source"] == "DEEPSEEK_API_KEY"
    assert "secret-deepseek-key" not in str(output)


def test_cli_check_provider_can_fail_on_unhealthy_config(monkeypatch, capsys):
    clear_provider_env(monkeypatch)
    monkeypatch.setattr(
        "sys.argv",
        ["qa-copilot", "--check-provider", "--fail-on-error"],
    )
    monkeypatch.setenv("AI_PROVIDER", "deepseek")

    with pytest.raises(SystemExit) as exc_info:
        cli_main()

    output = json.loads(capsys.readouterr().out)
    assert exc_info.value.code == 1
    assert output["ok"] is False
    assert output["missing"] == ["api_key"]


def test_cli_provider_commands_are_mutually_exclusive(monkeypatch):
    monkeypatch.setattr(
        "sys.argv",
        ["qa-copilot", "--list-providers", "--check-provider"],
    )

    with pytest.raises(SystemExit) as exc_info:
        cli_main()

    assert exc_info.value.code == 2

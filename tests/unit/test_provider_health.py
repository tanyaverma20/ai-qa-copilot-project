from __future__ import annotations

from qa_copilot.provider_health import check_provider_health
from tests.helpers import clear_provider_env


def test_check_provider_health_reports_missing_key(monkeypatch):
    clear_provider_env(monkeypatch)
    monkeypatch.setenv("AI_PROVIDER", "deepseek")

    health = check_provider_health()

    assert health["ok"] is False
    assert health["provider"] == "deepseek"
    assert health["api_style"] == "chat"
    assert health["errors"] == []
    assert health["missing"] == ["api_key"]


def test_check_provider_health_reports_detailed_config_without_leaking_key(monkeypatch):
    clear_provider_env(monkeypatch)
    monkeypatch.setenv("AI_PROVIDER", "deepseek")
    monkeypatch.setenv("DEEPSEEK_API_KEY", "secret-deepseek-key")

    health = check_provider_health(include_internal=True)

    assert health["ok"] is True
    assert health["provider"] == "deepseek"
    assert health["model"] == "deepseek-chat"
    assert health["base_url"] == "https://api.deepseek.com"
    assert health["api_style"] == "chat"
    assert health["api_key_configured"] is True
    assert health["api_key_source"] == "DEEPSEEK_API_KEY"
    assert "secret-deepseek-key" not in str(health)


def test_check_provider_health_rejects_unknown_provider(monkeypatch):
    clear_provider_env(monkeypatch)
    monkeypatch.setenv("AI_PROVIDER", "deepssek")
    monkeypatch.setenv("AI_API_KEY", "secret-generic-key")

    health = check_provider_health()

    assert health["ok"] is False
    assert health["provider"] == "deepssek"
    assert health["missing"] == []
    assert "unsupported_provider" in health["errors"]
    assert "secret-generic-key" not in str(health)


def test_check_provider_health_rejects_unknown_api_style(monkeypatch):
    clear_provider_env(monkeypatch)
    monkeypatch.setenv("AI_PROVIDER", "deepseek")
    monkeypatch.setenv("DEEPSEEK_API_KEY", "secret-deepseek-key")
    monkeypatch.setenv("AI_API_STYLE", "chta")

    health = check_provider_health()

    assert health["ok"] is False
    assert health["missing"] == []
    assert "unsupported_api_style" in health["errors"]


def test_check_provider_health_requires_base_url_for_openai_compatible(monkeypatch):
    clear_provider_env(monkeypatch)
    monkeypatch.setenv("AI_PROVIDER", "openai-compatible")
    monkeypatch.setenv("AI_API_KEY", "secret-gateway-key")

    health = check_provider_health()

    assert health["ok"] is False
    assert health["provider"] == "openai-compatible"
    assert health["errors"] == []
    assert health["missing"] == ["base_url"]


def test_check_provider_health_uses_generic_key_source_first(monkeypatch):
    clear_provider_env(monkeypatch)
    monkeypatch.setenv("AI_PROVIDER", "deepseek")
    monkeypatch.setenv("AI_API_KEY", "secret-generic-key")
    monkeypatch.setenv("DEEPSEEK_API_KEY", "secret-provider-key")

    health = check_provider_health(include_internal=True)

    assert health["ok"] is True
    assert health["api_key_source"] == "AI_API_KEY"
    assert "secret-generic-key" not in str(health)
    assert "secret-provider-key" not in str(health)

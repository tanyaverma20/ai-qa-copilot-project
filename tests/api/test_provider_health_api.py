from __future__ import annotations

from tests.helpers import clear_provider_env


def test_check_provider_health_api(client, monkeypatch):
    clear_provider_env(monkeypatch)
    monkeypatch.setenv("AI_PROVIDER", "deepseek")
    monkeypatch.setenv("DEEPSEEK_API_KEY", "secret-deepseek-key")

    response = client.get("/api/provider-health")

    assert response.status_code == 200
    payload = response.json()
    assert payload["ok"] is True
    assert payload["provider"] == "deepseek"
    assert payload["api_style"] == "chat"
    assert payload["api_key_configured"] is True
    assert payload["missing"] == []
    assert payload["errors"] == []
    assert "api_key_source" not in payload
    assert "base_url" not in payload
    assert "model" not in payload
    assert "secret-deepseek-key" not in str(payload)


def test_check_provider_health_api_redacts_internal_config(client, monkeypatch):
    clear_provider_env(monkeypatch)
    monkeypatch.setenv("AI_PROVIDER", "openai-compatible")
    monkeypatch.setenv("AI_API_KEY", "secret-gateway-key")
    monkeypatch.setenv("AI_BASE_URL", "https://tenant.internal.example/v1")
    monkeypatch.setenv("AI_MODEL", "tenant-routed-model")

    response = client.get("/api/provider-health")

    assert response.status_code == 200
    payload = response.json()
    assert payload == {
        "ok": True,
        "provider": "openai-compatible",
        "api_style": "chat",
        "api_key_configured": True,
        "missing": [],
        "errors": [],
    }
    assert "secret-gateway-key" not in str(payload)
    assert "AI_API_KEY" not in str(payload)
    assert "tenant.internal.example" not in str(payload)
    assert "tenant-routed-model" not in str(payload)

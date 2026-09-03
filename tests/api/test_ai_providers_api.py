from __future__ import annotations


def test_list_ai_providers(client):
    response = client.get("/api/ai-providers")

    assert response.status_code == 200
    payload = response.json()
    assert "deepseek" in payload["providers"]
    assert payload["providers"]["deepseek"]["api_style"] == "chat"
    assert payload["providers"]["openai"]["api_style"] == "responses"

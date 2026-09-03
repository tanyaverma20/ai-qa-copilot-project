from __future__ import annotations

from qa_copilot.providers import (
    DiagnosisProviderConfig,
    OpenAICompatibleChatProvider,
    OpenAIResponsesProvider,
    create_diagnosis_provider,
    supported_provider_specs,
)


class FakeResponses:
    def __init__(self):
        self.calls: list[dict[str, str]] = []

    def create(self, model: str, input: str):  # noqa: A002
        self.calls.append({"model": model, "input": input})
        return type("Response", (), {"output_text": "## Summary\n\nAPI diagnosis"})()


class FakeOpenAIClient:
    def __init__(self):
        self.responses = FakeResponses()


class FakeChatCompletions:
    def __init__(self):
        self.calls: list[dict[str, object]] = []

    def create(self, model: str, messages: list[dict[str, str]], temperature: float):
        self.calls.append({"model": model, "messages": messages, "temperature": temperature})
        message = type("Message", (), {"content": "chat diagnosis"})()
        choice = type("Choice", (), {"message": message})()
        return type("Response", (), {"choices": [choice]})()


class FakeChat:
    def __init__(self):
        self.completions = FakeChatCompletions()


class FakeChatClient:
    def __init__(self):
        self.chat = FakeChat()


def test_config_from_env_reads_openai_settings(monkeypatch):
    monkeypatch.setenv("AI_PROVIDER", "openai")
    monkeypatch.setenv("AI_API_KEY", "test-key")
    monkeypatch.setenv("AI_MODEL", "gpt-test")
    monkeypatch.setenv("AI_BASE_URL", "https://gateway.example.test/v1")

    config = DiagnosisProviderConfig.from_env()

    assert config.provider == "openai"
    assert config.api_key == "test-key"
    assert config.model == "gpt-test"
    assert config.base_url == "https://gateway.example.test/v1"
    assert config.api_style == "responses"


def test_config_from_env_uses_deepseek_preset(monkeypatch):
    monkeypatch.setenv("AI_PROVIDER", "deepseek")
    monkeypatch.setenv("DEEPSEEK_API_KEY", "deepseek-key")
    monkeypatch.delenv("AI_MODEL", raising=False)
    monkeypatch.delenv("AI_BASE_URL", raising=False)

    config = DiagnosisProviderConfig.from_env()

    assert config.provider == "deepseek"
    assert config.api_key == "deepseek-key"
    assert config.model == "deepseek-chat"
    assert config.base_url == "https://api.deepseek.com"
    assert config.api_style == "chat"


def test_openai_responses_provider_sends_prompt_to_responses_api():
    client = FakeOpenAIClient()
    provider = OpenAIResponsesProvider(
        config=DiagnosisProviderConfig(api_key="test-key", model="gpt-test"),
        client=client,
    )

    result = provider.generate("failure prompt")

    assert result == "## Summary\n\nAPI diagnosis"
    assert client.responses.calls == [{"model": "gpt-test", "input": "failure prompt"}]


def test_openai_compatible_chat_provider_sends_prompt_to_chat_completions():
    client = FakeChatClient()
    provider = OpenAICompatibleChatProvider(
        config=DiagnosisProviderConfig(
            provider="deepseek",
            api_key="test-key",
            model="deepseek-chat",
            base_url="https://api.deepseek.com",
            api_style="chat",
        ),
        client=client,
    )

    result = provider.generate("failure prompt")

    assert result == "chat diagnosis"
    assert client.chat.completions.calls == [
        {
            "model": "deepseek-chat",
            "messages": [
                {
                    "role": "system",
                    "content": "You are an expert QA failure diagnosis assistant.",
                },
                {"role": "user", "content": "failure prompt"},
            ],
            "temperature": 0.2,
        }
    ]


def test_create_diagnosis_provider_selects_chat_adapter_for_deepseek():
    config = DiagnosisProviderConfig(
        provider="deepseek",
        api_key="test-key",
        model="deepseek-chat",
        base_url="https://api.deepseek.com",
        api_style="chat",
    )

    provider = create_diagnosis_provider(config)

    assert isinstance(provider, OpenAICompatibleChatProvider)


def test_supported_provider_specs_exposes_public_provider_metadata():
    providers = supported_provider_specs()

    deepseek = providers["deepseek"]
    assert deepseek["api_style"] == "chat"
    assert deepseek["default_model"] == "deepseek-chat"
    assert deepseek["default_base_url"] == "https://api.deepseek.com"
    assert deepseek["api_key_env_names"] == ["DEEPSEEK_API_KEY"]
    assert "api_key" not in deepseek

from __future__ import annotations

PROVIDER_ENV_NAMES = (
    "AI_PROVIDER",
    "AI_API_KEY",
    "AI_MODEL",
    "AI_BASE_URL",
    "AI_API_STYLE",
    "OPENAI_API_KEY",
    "OPENAI_MODEL",
    "OPENAI_BASE_URL",
    "DEEPSEEK_API_KEY",
    "DASHSCOPE_API_KEY",
    "QWEN_API_KEY",
    "MOONSHOT_API_KEY",
    "KIMI_API_KEY",
    "SILICONFLOW_API_KEY",
    "OPENROUTER_API_KEY",
    "ARK_API_KEY",
    "VOLCENGINE_API_KEY",
    "DOUBAO_API_KEY",
)


def clear_provider_env(monkeypatch) -> None:
    for name in PROVIDER_ENV_NAMES:
        monkeypatch.delenv(name, raising=False)

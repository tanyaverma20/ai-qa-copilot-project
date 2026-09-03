from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any, Protocol

from openai import OpenAI


class DiagnosisProvider(Protocol):
    def generate(self, prompt: str) -> str:
        """Generate a diagnosis report from a failure prompt."""


@dataclass(frozen=True)
class ProviderPreset:
    default_model: str
    api_style: str
    default_base_url: str | None
    api_key_env_names: tuple[str, ...]


PROVIDER_PRESETS: dict[str, ProviderPreset] = {
    "openai": ProviderPreset(
        default_model="gpt-4.1-mini",
        api_style="responses",
        default_base_url=None,
        api_key_env_names=("OPENAI_API_KEY",),
    ),
    "deepseek": ProviderPreset(
        default_model="deepseek-chat",
        api_style="chat",
        default_base_url="https://api.deepseek.com",
        api_key_env_names=("DEEPSEEK_API_KEY",),
    ),
    "qwen": ProviderPreset(
        default_model="qwen-plus",
        api_style="chat",
        default_base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        api_key_env_names=("DASHSCOPE_API_KEY", "QWEN_API_KEY"),
    ),
    "dashscope": ProviderPreset(
        default_model="qwen-plus",
        api_style="chat",
        default_base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        api_key_env_names=("DASHSCOPE_API_KEY", "QWEN_API_KEY"),
    ),
    "kimi": ProviderPreset(
        default_model="kimi-k2-0711-preview",
        api_style="chat",
        default_base_url="https://api.moonshot.cn/v1",
        api_key_env_names=("MOONSHOT_API_KEY", "KIMI_API_KEY"),
    ),
    "moonshot": ProviderPreset(
        default_model="kimi-k2-0711-preview",
        api_style="chat",
        default_base_url="https://api.moonshot.cn/v1",
        api_key_env_names=("MOONSHOT_API_KEY", "KIMI_API_KEY"),
    ),
    "siliconflow": ProviderPreset(
        default_model="deepseek-ai/DeepSeek-V3",
        api_style="chat",
        default_base_url="https://api.siliconflow.cn/v1",
        api_key_env_names=("SILICONFLOW_API_KEY",),
    ),
    "openrouter": ProviderPreset(
        default_model="deepseek/deepseek-chat-v3.1",
        api_style="chat",
        default_base_url="https://openrouter.ai/api/v1",
        api_key_env_names=("OPENROUTER_API_KEY",),
    ),
    "doubao": ProviderPreset(
        default_model="doubao-seed-1-6",
        api_style="chat",
        default_base_url="https://ark.cn-beijing.volces.com/api/v3",
        api_key_env_names=("ARK_API_KEY", "VOLCENGINE_API_KEY", "DOUBAO_API_KEY"),
    ),
    "openai-compatible": ProviderPreset(
        default_model="gpt-4.1-mini",
        api_style="chat",
        default_base_url=None,
        api_key_env_names=("AI_API_KEY", "OPENAI_API_KEY"),
    ),
}


@dataclass(frozen=True)
class DiagnosisProviderConfig:
    api_key: str
    provider: str = "openai"
    model: str = "gpt-4.1-mini"
    base_url: str | None = None
    api_style: str = "responses"

    @classmethod
    def from_env(cls) -> DiagnosisProviderConfig:
        provider = os.getenv("AI_PROVIDER", "openai").strip().lower() or "openai"
        preset = PROVIDER_PRESETS.get(provider, PROVIDER_PRESETS["openai"])
        api_key = _first_env_value(("AI_API_KEY", *preset.api_key_env_names))
        model = (
            os.getenv("AI_MODEL", "").strip()
            or os.getenv("OPENAI_MODEL", "").strip()
            or preset.default_model
        )
        base_url = (
            os.getenv("AI_BASE_URL", "").strip()
            or os.getenv("OPENAI_BASE_URL", "").strip()
            or preset.default_base_url
        )
        return cls(
            provider=provider,
            api_key=api_key,
            model=model,
            base_url=base_url,
            api_style=os.getenv("AI_API_STYLE", "").strip().lower() or preset.api_style,
        )


def _first_env_value(names: tuple[str, ...]) -> str:
    for name in names:
        value = os.getenv(name, "").strip()
        if value:
            return value
    return ""


def supported_provider_specs() -> dict[str, dict[str, object]]:
    return {
        name: {
            "default_model": preset.default_model,
            "api_style": preset.api_style,
            "default_base_url": preset.default_base_url,
            "api_key_env_names": list(preset.api_key_env_names),
        }
        for name, preset in sorted(PROVIDER_PRESETS.items())
    }


class OpenAIResponsesProvider:
    def __init__(
        self,
        config: DiagnosisProviderConfig,
        client: Any | None = None,
    ) -> None:
        self.config = config
        self.client = client

    def _client(self) -> Any:
        if self.client is not None:
            return self.client
        if self.config.base_url:
            return OpenAI(api_key=self.config.api_key, base_url=self.config.base_url)
        return OpenAI(api_key=self.config.api_key)

    def generate(self, prompt: str) -> str:
        response = self._client().responses.create(
            model=self.config.model,
            input=prompt,
        )
        return str(response.output_text)


class OpenAICompatibleChatProvider:
    def __init__(
        self,
        config: DiagnosisProviderConfig,
        client: Any | None = None,
    ) -> None:
        self.config = config
        self.client = client

    def _client(self) -> Any:
        if self.client is not None:
            return self.client
        if self.config.base_url:
            return OpenAI(api_key=self.config.api_key, base_url=self.config.base_url)
        return OpenAI(api_key=self.config.api_key)

    def generate(self, prompt: str) -> str:
        response = self._client().chat.completions.create(
            model=self.config.model,
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert QA failure diagnosis assistant.",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.2,
        )
        return str(response.choices[0].message.content)


def create_diagnosis_provider(config: DiagnosisProviderConfig) -> DiagnosisProvider:
    if config.api_style == "chat":
        return OpenAICompatibleChatProvider(config)
    return OpenAIResponsesProvider(config)

from __future__ import annotations

import os
from typing import Any

from qa_copilot.providers import PROVIDER_PRESETS, DiagnosisProviderConfig

SUPPORTED_API_STYLES = {"chat", "responses"}


def _configured_key_source(provider: str) -> str | None:
    preset = PROVIDER_PRESETS.get(provider)
    provider_key_names = preset.api_key_env_names if preset else ()
    for name in ("AI_API_KEY", *provider_key_names):
        if os.getenv(name, "").strip():
            return name
    return None


def validate_provider_config(config: DiagnosisProviderConfig) -> list[str]:
    _, errors = provider_config_issues(config)
    return errors


def provider_config_issues(
    config: DiagnosisProviderConfig,
) -> tuple[list[str], list[str]]:
    missing: list[str] = []
    errors: list[str] = []
    if config.provider not in PROVIDER_PRESETS:
        errors.append("unsupported_provider")
    if config.api_style not in SUPPORTED_API_STYLES:
        errors.append("unsupported_api_style")
    if not config.api_key:
        missing.append("api_key")
    if not config.model:
        missing.append("model")
    if config.api_style == "chat" and not config.base_url:
        missing.append("base_url")
    return missing, errors


def check_provider_health(*, include_internal: bool = False) -> dict[str, Any]:
    config = DiagnosisProviderConfig.from_env()
    key_source = _configured_key_source(config.provider)
    missing, errors = provider_config_issues(config)

    payload: dict[str, Any] = {
        "ok": not missing and not errors,
        "provider": config.provider,
        "api_style": config.api_style,
        "api_key_configured": bool(config.api_key),
        "missing": missing,
        "errors": errors,
    }

    if include_internal:
        payload.update(
            {
                "model": config.model,
                "base_url": config.base_url,
                "api_key_source": key_source,
            }
        )

    return payload

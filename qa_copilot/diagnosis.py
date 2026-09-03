from __future__ import annotations

from qa_copilot.provider_health import provider_config_issues
from qa_copilot.providers import (
    DiagnosisProvider,
    DiagnosisProviderConfig,
    create_diagnosis_provider,
)


def fallback_report(reason: str) -> str:
    return f"""## Summary

AI diagnosis was skipped because {reason}.

## Suspected root cause

Review the pytest failure artifact manually.

## Reproduction steps

Run the failing pytest node shown in the failure artifact.

## Evidence

The local pytest report and JSON failure artifact are available in reports/latest.

## Suggested fix

Inspect the failed assertion, request payload, response body, and browser trace.

## Risk level

Unknown

## Classification

environment issue
"""


def diagnose_with_ai(
    prompt: str,
    provider: DiagnosisProvider | None = None,
    config: DiagnosisProviderConfig | None = None,
) -> str:
    resolved_config = config or DiagnosisProviderConfig.from_env()
    missing_config, config_errors = provider_config_issues(resolved_config)
    if config_errors:
        return fallback_report(", ".join(config_errors))
    if "api_key" in missing_config:
        return fallback_report("API key is not configured")
    if missing_config:
        return fallback_report(f"provider config is missing: {', '.join(missing_config)}")

    try:
        resolved_provider = provider or create_diagnosis_provider(resolved_config)
        return resolved_provider.generate(prompt)
    except Exception as exc:
        return fallback_report(str(exc))

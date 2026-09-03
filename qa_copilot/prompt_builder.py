from __future__ import annotations

from collections import defaultdict

from qa_copilot.artifacts import FailureArtifact

FAILURE_MODE_ORDER = (
    "Product/API behavior",
    "API contract",
    "UI/E2E behavior",
    "Flaky/timing",
    "Environment/setup",
    "Unclassified",
)


def _failure_mode(artifact: FailureArtifact) -> str:
    keywords = {keyword.lower() for keyword in artifact.keywords}
    phase = artifact.phase.lower()

    if phase == "setup" or keywords.intersection({"fixture", "setup"}):
        return "Environment/setup"
    if "flaky" in keywords:
        return "Flaky/timing"
    if keywords.intersection({"api-assertion", "contract"}):
        return "API contract"
    if keywords.intersection({"playwright", "e2e", "visibility"}):
        return "UI/E2E behavior"
    if "api" in keywords:
        return "Product/API behavior"
    return "Unclassified"


def _group_by_failure_mode(
    artifacts: list[FailureArtifact],
) -> dict[str, list[FailureArtifact]]:
    grouped: dict[str, list[FailureArtifact]] = defaultdict(list)
    for artifact in artifacts:
        grouped[_failure_mode(artifact)].append(artifact)
    return {mode: grouped[mode] for mode in FAILURE_MODE_ORDER if grouped[mode]}


def build_diagnosis_prompt(artifacts: list[FailureArtifact]) -> str:
    sections = [
        "You are an AI QA copilot helping diagnose automated test failures.",
        "Return a structured report with these headings:",
        "- Summary",
        "- Failure mode matrix",
        "- Suspected root cause",
        "- Reproduction steps",
        "- Evidence",
        "- Suggested fix",
        "- Risk level",
        "- Classification: product bug, test script bug, flaky test, or environment issue",
        "",
        "In the failure mode matrix, include columns for failure mode, affected test, "
        "evidence, likely classification, and next action.",
        "",
        "Failure mode groups:",
    ]
    for mode, grouped_artifacts in _group_by_failure_mode(artifacts).items():
        sections.extend(["", f"### {mode}"])
        for artifact in grouped_artifacts:
            sections.extend(
                [
                    f"Test: {artifact.nodeid}",
                    f"Failed at: {artifact.failed_at}",
                    f"Phase: {artifact.phase}",
                    f"Duration seconds: {artifact.duration_seconds}",
                    f"Keywords: {', '.join(artifact.keywords)}",
                    "Trace:",
                    artifact.longrepr,
                    "",
                ]
            )
    if not artifacts:
        sections.extend(
            [
                "",
                "No failure artifacts were provided.",
            ]
        )
    return "\n".join(sections)

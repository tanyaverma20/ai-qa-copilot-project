from __future__ import annotations

import argparse
import re
from pathlib import Path

DEFAULT_ARTIFACT_HINT = (
    "See uploaded CI artifacts for pytest reports, failure JSON, screenshots, "
    "and traces when available."
)
SECRET_PATTERNS = (
    re.compile(r"sk-[A-Za-z0-9_-]+"),
    re.compile(r"Bearer\s+[A-Za-z0-9._-]+"),
    re.compile(r"(?i)(authorization\s*:\s*)\S+"),
    re.compile(r"(?i)((?:api[_-]?key|password|cookie)\s*[:=]\s*)\S+"),
    re.compile(r"\b[A-Z0-9_]*(?:API_KEY|TOKEN|SECRET)[A-Z0-9_]*\b"),
    re.compile(r"https?://(?:[^\s/]*internal[^\s/]*|tenant\.[^\s/]+)[^\s]*", re.I),
)


def extract_section(markdown: str, heading: str) -> str:
    """Return a Markdown section body by heading text."""
    lines = markdown.splitlines()
    start_index: int | None = None
    start_level = 0

    for index, line in enumerate(lines):
        match = re.match(r"^(#{1,6})\s+(.+?)\s*$", line)
        if not match:
            continue
        if match.group(2).strip().casefold() == heading.casefold():
            start_index = index + 1
            start_level = len(match.group(1))
            break

    if start_index is None:
        return ""

    end_index = len(lines)
    for index in range(start_index, len(lines)):
        match = re.match(r"^(#{1,6})\s+(.+?)\s*$", lines[index])
        if match and len(match.group(1)) <= start_level:
            end_index = index
            break

    return "\n".join(lines[start_index:end_index]).strip()


def redact_comment_text(text: str) -> str:
    redacted = text
    for pattern in SECRET_PATTERNS:
        if pattern.groups >= 1:
            redacted = pattern.sub(lambda match: f"{match.group(1)}[REDACTED]", redacted)
        else:
            redacted = pattern.sub("[REDACTED]", redacted)
    return redacted


def _first_available_section(markdown: str, headings: tuple[str, ...]) -> str:
    for heading in headings:
        section = extract_section(markdown, heading)
        if section:
            return section
    return ""


def _normalize_recommended_steps(section: str) -> str:
    if not section:
        return (
            "1. Review the full AI diagnosis report.\n"
            "2. Inspect the uploaded test artifacts.\n"
            "3. Assign follow-up work based on the failure mode classification."
        )
    return section


def build_pr_comment(
    diagnosis_markdown: str,
    *,
    artifact_hint: str = DEFAULT_ARTIFACT_HINT,
) -> str:
    summary = extract_section(diagnosis_markdown, "Summary") or (
        "No summary was found in the diagnosis report."
    )
    matrix = extract_section(diagnosis_markdown, "Failure Mode Matrix") or (
        "_No failure mode matrix was found in the diagnosis report._"
    )
    recommended_steps = _first_available_section(
        diagnosis_markdown,
        ("Recommended next steps", "Suggested fix", "Suggested fixes"),
    )

    comment = f"""## AI QA Copilot Diagnosis Preview

> Dry-run PR comment preview. No GitHub API call was made.

### Summary

{summary}

### Failure Mode Matrix

{matrix}

### Recommended next steps

{_normalize_recommended_steps(recommended_steps)}

### Artifacts

- {artifact_hint}

### Safety

This preview applies basic secret-like redaction and avoids including full raw traces by default.
It does not call the GitHub API or require a GitHub token.
Review generated comments before posting to public PRs, especially if diagnosis reports may contain
proprietary logs, internal URLs, model names, or provider configuration details.
"""
    return redact_comment_text(comment).strip() + "\n"


def write_pr_comment(
    diagnosis_path: str | Path,
    output_path: str | Path,
    *,
    artifact_hint: str = DEFAULT_ARTIFACT_HINT,
) -> None:
    diagnosis_text = Path(diagnosis_path).read_text(encoding="utf-8")
    comment = build_pr_comment(diagnosis_text, artifact_hint=artifact_hint)
    destination = Path(output_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(comment, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate a dry-run GitHub PR comment preview from an AI diagnosis report."
    )
    parser.add_argument("--input", default="reports/examples/sample-ai-diagnosis.md")
    parser.add_argument("--output", default="reports/latest/demo-pr-comment.md")
    parser.add_argument("--artifact-hint", default=DEFAULT_ARTIFACT_HINT)
    args = parser.parse_args()

    write_pr_comment(args.input, args.output, artifact_hint=args.artifact_hint)


if __name__ == "__main__":
    main()

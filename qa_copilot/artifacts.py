from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class FailureArtifact:
    nodeid: str
    failed_at: str
    phase: str
    duration_seconds: float
    longrepr: str
    keywords: list[str]


def load_failure_artifacts(path: str | Path) -> list[FailureArtifact]:
    root = Path(path)
    if not root.exists():
        return []

    artifacts: list[FailureArtifact] = []
    for artifact_file in sorted(root.glob("*.json")):
        try:
            payload = json.loads(artifact_file.read_text(encoding="utf-8"))
            artifacts.append(
                FailureArtifact(
                    nodeid=str(payload["nodeid"]),
                    failed_at=str(payload["failed_at"]),
                    phase=str(payload["phase"]),
                    duration_seconds=float(payload["duration_seconds"]),
                    longrepr=str(payload["longrepr"]),
                    keywords=[str(keyword) for keyword in payload.get("keywords", [])],
                )
            )
        except (json.JSONDecodeError, KeyError, TypeError, ValueError):
            continue
    return artifacts

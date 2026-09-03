from __future__ import annotations

from pathlib import Path


def write_markdown_report(path: str | Path, title: str, body: str) -> None:
    report_path = Path(path)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(f"# {title}\n\n{body.rstrip()}\n", encoding="utf-8")

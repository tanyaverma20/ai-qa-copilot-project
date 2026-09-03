from __future__ import annotations

from qa_copilot.report_writer import write_markdown_report


def test_write_markdown_report(tmp_path):
    output = tmp_path / "diagnosis.md"

    write_markdown_report(
        output,
        title="AI Diagnosis Report",
        body="## Summary\n\nThe order API returned 500.",
    )

    assert output.read_text(encoding="utf-8") == (
        "# AI Diagnosis Report\n\n"
        "## Summary\n\n"
        "The order API returned 500.\n"
    )

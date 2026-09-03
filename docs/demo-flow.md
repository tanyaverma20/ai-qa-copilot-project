# Demo Failure Flow

This project includes curated failure artifacts so reviewers can see the AI diagnosis workflow without breaking the test suite.

## Generate A Demo Diagnosis Report

Run:

```powershell
python -m qa_copilot.cli --input reports/examples --output reports/latest/demo-ai-diagnosis.md
```

Then open:

```powershell
Get-Content reports/latest/demo-ai-diagnosis.md
```

You can also generate a dry-run PR comment preview from the curated diagnosis report:

```powershell
python -m qa_copilot.pr_comment --input reports/examples/sample-ai-diagnosis.md --output reports/latest/demo-pr-comment.md
```

The committed preview is available at:

```text
reports/examples/sample-pr-comment.md
```

This preview is Markdown only. It does not call GitHub PR/Issues API, does not need `GITHUB_TOKEN`, and does not post comments.

If `OPENAI_API_KEY` is not configured, the command writes a fallback report. This is intentional: the automation workflow should still complete even when AI access is unavailable.

If `OPENAI_API_KEY` is configured, the same command sends the sample failure context to the configured OpenAI model and writes a generated diagnosis report.

## What The Demo Shows

The sample artifacts cover several realistic QA failure modes:

- an insufficient-stock API test that expected HTTP `409` but received HTTP `500`
- a Playwright visibility failure with screenshot and trace references
- an API contract mismatch with request and response evidence
- a flaky search test with repeated pass/fail history
- a database fixture/setup failure

The generated report is expected to start with a failure mode matrix, then explain the likely root cause, evidence, reproduction steps, suggested fix, risk level, and whether each failure looks like a product bug, test script bug, flaky test, or environment issue.

See [diagnosis-examples.md](diagnosis-examples.md) for the full example catalog.

## Real CI Flow

In real test runs, `tests/conftest.py` writes failed test artifacts to:

```text
reports/latest/failures/
```

GitHub Actions then runs:

```powershell
python -m qa_copilot.cli --input reports/latest/failures --output reports/latest/ai-diagnosis.md
```

It also generates a dry-run PR comment preview:

```powershell
python -m qa_copilot.pr_comment --input reports/latest/ai-diagnosis.md --output reports/latest/pr-comment.md
```

The resulting report and PR comment preview are uploaded inside the `qa-reports` artifact.

A future workflow can post that generated Markdown to GitHub, but posting is intentionally out of scope for the current demo.

`pr-comment.md` applies basic redaction, but CI artifacts may still contain raw test logs or traces. Review artifacts before using this workflow with proprietary systems.

For a file-by-file artifact guide, see [CI Artifacts](ci-artifacts.md).

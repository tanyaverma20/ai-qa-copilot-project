# CI Artifacts

GitHub Actions uploads a `qa-reports` artifact for each CI run. This guide explains where to find it, which files matter, and how to talk about them in a portfolio review.

## Where to find them

Open the latest GitHub Actions run, scroll to **Artifacts**, and download `qa-reports`.

The artifact is produced from the repository's `reports/` directory after the workflow runs tests, generates an AI diagnosis report, and creates a dry-run PR comment preview.

For a stable portfolio demo, use the **Demo Artifacts** workflow from the GitHub Actions tab. It is started manually with `workflow_dispatch` and uploads `demo-qa-reports`.

`demo-qa-reports` is a curated demo artifact built from `reports/examples` and `reports/examples/sample-ai-diagnosis.md`. It is useful for interviews because it always includes example failure JSON, an AI diagnosis sample, and a dry-run PR comment preview without requiring a failing CI run.

The manual demo workflow does not call GitHub PR/Issues API, does not post comments, and does not use repository secrets or external AI provider keys.

## What is inside

| File | Purpose | Interview talking point |
| --- | --- | --- |
| `reports/latest/pytest-report.html` | Human-readable pytest report | Shows automated test execution results in CI. |
| `reports/latest/failures/*.json` | Structured failure artifacts | Provides the input evidence for AI diagnosis. |
| `reports/latest/ai-diagnosis.md` | Full AI diagnosis or fallback report | Shows root cause hypotheses, evidence, suggested fixes, and failure classification. |
| `reports/latest/pr-comment.md` | Dry-run PR comment preview | Shows how the diagnosis can become a concise PR review summary. |
| Playwright screenshots / traces | Browser failure evidence when available | Helps debug UI/E2E failures with visual and trace context. |

## How to explain it

Use the artifact as the CI proof of the project workflow:

```text
pytest / Playwright
-> pytest-report.html
-> failures/*.json
-> ai-diagnosis.md
-> pr-comment.md
-> qa-reports artifact
```

The main interview message is that the project does more than run tests. It preserves test evidence, converts failure artifacts into an AI diagnosis, and prepares a review-friendly PR comment preview without posting to GitHub automatically.

For the manual demo artifact, be explicit that it is curated sample data:

```text
reports/examples
-> reports/demo/failures
-> reports/demo/ai-diagnosis.md
-> reports/demo/pr-comment.md
-> demo-qa-reports artifact
```

Use `qa-reports` to discuss real CI output. Use `demo-qa-reports` when you want a reproducible portfolio walkthrough from curated examples.

## Safety boundary

`reports/latest/pr-comment.md` is generated through the PR comment preview generator and applies basic redaction.

The full `qa-reports` artifact may still contain raw test logs, failure JSON, screenshots, traces, request/response snippets, or stack traces. Review artifacts before using this workflow with proprietary systems.

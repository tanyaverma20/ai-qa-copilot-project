# Portfolio Walkthrough

This walkthrough is the shortest path for showing AI QA Copilot in an interview or portfolio review. It connects the visible demo app, provider safety checks, test automation artifacts, and AI diagnosis output into one story.

## 3-Minute Interview Path

1. Open the Chinese Showcase Dashboard at `/`.
2. Explain the visible project path: Dashboard -> Demo Shop order -> QA reports -> AI diagnosis -> dry-run PR comment preview.
3. Enter the Demo Shop, log in with the demo account, and create an order.
4. Use the order-success page to explain that the shop is the system under test, not the final product goal.
5. Point out the Provider Status card: it shows readiness without exposing API keys, model names, key source environment variables, or custom base URLs.
6. Run the bundled failure examples through the CLI.
7. Open the generated report or the curated sample report.
8. Explain the Failure Mode Matrix: it separates product/API bugs, contract drift, UI/E2E failures, flaky timing, and environment/setup failures.
9. Optionally open the PR comment preview to show how the diagnosis could fit a code review workflow.

## Run The Demo App

```powershell
uvicorn app.main:app --reload
```

Open:

```text
http://127.0.0.1:8000
```

Demo account:

```text
username: alice
password: password123
```

These are local demo credentials only; do not reuse them in production.

The products page includes Provider Status. The same provider health data is also available from the redacted API endpoint:

![Provider Status card](assets/provider-status.png)

```powershell
Invoke-RestMethod http://127.0.0.1:8000/api/provider-health
```

## What Happens After Buying A Product

The order flow is intentionally small. It exists as the system under test for API and Playwright E2E automation.

When the order succeeds, the success page explains the next step: the order path proves the demo system can be exercised by a browser test. If login, product loading, inventory, or order creation fails, the project can preserve the failure as structured evidence and turn it into a diagnosis report.

The interview message is:

```text
Buying a product is not the product goal.
It is the real business path used to demonstrate automated testing and failure diagnosis.
```

## Generate A Diagnosis Demo

The repo includes safe example artifacts in `reports/examples/`, so the demo does not require intentionally breaking the test suite.

```powershell
python -m qa_copilot.cli --input reports/examples --output reports/latest/demo-ai-diagnosis.md
```

Without a configured provider key, the command writes a fallback report. With a configured provider, it sends grouped failure context to the provider.

Use a temporary demo key, and avoid sending proprietary logs to third-party providers.

DeepSeek example:

```powershell
$env:AI_PROVIDER="deepseek"
$env:DEEPSEEK_API_KEY="your-deepseek-key"
python -m qa_copilot.cli --input reports/examples --output reports/latest/demo-ai-diagnosis.md
```

Open the generated report:

```powershell
Get-Content reports/latest/demo-ai-diagnosis.md
```

For a stable portfolio example, use:

```text
reports/examples/sample-ai-diagnosis.md
```

To regenerate the committed preview images, see [Screenshot Capture](screenshots.md).

## Optional PR Comment Preview

Turn the curated diagnosis report into a dry-run GitHub PR comment preview:

```powershell
python -m qa_copilot.pr_comment --input reports/examples/sample-ai-diagnosis.md --output reports/latest/demo-pr-comment.md
```

For a stable portfolio example, use:

```text
reports/examples/sample-pr-comment.md
```

This preview does not call GitHub PR/Issues API, does not need a token, and does not post comments. It shows the next integration step: test failure artifacts become an AI diagnosis report, then a concise review comment.

In GitHub Actions, the same dry-run preview is uploaded as `reports/latest/pr-comment.md` inside the `qa-reports` artifact. It does not post comments.

When showing CI, open the `qa-reports` artifact and point to `pytest-report.html`, `ai-diagnosis.md`, and `pr-comment.md`. See [CI Artifacts](ci-artifacts.md) for the file-by-file guide.

## What To Show

Use the Failure Mode Matrix as the centerpiece:

![Failure Mode Matrix](assets/failure-mode-matrix.png)

| Failure Mode | What It Demonstrates |
| --- | --- |
| Product/API behavior | A business error returns the wrong HTTP status. |
| API contract | Request/response shape drifts from the expected contract. |
| UI/E2E behavior | A browser-visible control is hidden or not ready. |
| Flaky/timing | Repeated CI history shows unstable timing behavior. |
| Environment/setup | The test fails before assertions because setup is broken. |

The interview message is simple: this project is not just a collection of tests. It captures failure evidence, protects provider configuration, and turns automated-test output into a structured diagnosis workflow.

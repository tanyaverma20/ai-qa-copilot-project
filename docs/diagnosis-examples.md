# AI Diagnosis Example Catalog

The `reports/examples/` directory contains curated failure artifacts for portfolio demos. They are intentionally small, realistic, and safe to run without breaking the test suite.

Generate a demo diagnosis from all examples:

```powershell
python -m qa_copilot.cli --input reports/examples --output reports/latest/demo-ai-diagnosis.md
```

If no provider key is configured, the command writes a fallback report. With a configured provider, the prompt asks for a failure mode matrix and groups the example contexts before sending them to the AI provider.

| File | Scenario | What It Demonstrates |
| --- | --- | --- |
| `sample-failure.json` | Insufficient-stock order returns HTTP `500` instead of `409` | Product bug classification from API status mismatch |
| `playwright-visibility-failure.json` | Checkout `Pay now` button is hidden | Playwright locator failure with screenshot and trace references |
| `api-contract-failure.json` | Order creation contract returns `422` instead of `201` | API request/response evidence and contract mismatch |
| `flaky-search-failure.json` | Product search intermittently returns inconsistent counts | Flaky-test diagnosis from repeated pass/fail history |
| `fixture-setup-failure.json` | Database seed fixture fails during setup | Fixture/setup failure before test assertions run |

These examples are meant to help an interviewer see that the project is more than a test runner: it captures enough context for an AI assistant to separate product bugs, test bugs, timing problems, and environment/setup failures.

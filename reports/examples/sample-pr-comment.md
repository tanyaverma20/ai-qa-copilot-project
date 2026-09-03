## AI QA Copilot Diagnosis Preview

> Dry-run PR comment preview. No GitHub API call was made.

### Summary

The example artifact set shows five common QA failure modes: API status mismatch, Playwright visibility failure, API contract mismatch, flaky UI timing, and fixture/setup failure.

### Failure Mode Matrix

| Failure Mode | Affected Test / Artifact | Evidence | Likely Classification | Next Action |
| --- | --- | --- | --- | --- |
| Product/API behavior | `tests/api/test_orders_api.py::test_create_order_rejects_insufficient_stock` / `sample-failure.json` | Expected `409`, received `500` | Product bug | Map insufficient-stock domain errors to HTTP `409`. |
| API contract | `tests/api/test_orders_api.py::test_create_order_contract` / `api-contract-failure.json` | `POST /api/orders` returned `422`; response says `quantity` is missing | Product bug or test contract drift | Compare request body, validation schema, and expected response contract. |
| UI/E2E behavior | `tests/e2e/test_checkout_flow.py::test_checkout_button_enables_payment` / `playwright-visibility-failure.json` | `Pay now` button expected visible but was hidden | Product bug or UI readiness bug | Inspect checkout state, screenshot, and trace around the hidden button. |
| Flaky/timing | `tests/e2e/test_product_search.py::test_search_filters_results` / `flaky-search-failure.json` | Passed 7 times and failed 3 times over 10 CI runs | Flaky test | Wait on stable search results instead of racing debounce and fetch state. |
| Environment/setup | `tests/conftest.py::db_seed_fixture` / `fixture-setup-failure.json` | `sqlite3.OperationalError: no such table: products` during setup | Environment issue | Ensure database initialization runs before seed fixtures touch `products`. |

### Recommended next steps

- Map domain errors to explicit API responses.
- Add UI readiness checks around checkout state transitions.
- Keep API tests aligned with the public request/response schema.
- Make flaky UI assertions wait on stable app state instead of transient counts.
- Ensure database initialization runs before seed fixtures.

### Artifacts

- Full diagnosis report: reports/examples/sample-ai-diagnosis.md; failure artifacts: reports/examples/*.json; in CI, see uploaded pytest reports, screenshots, traces, and failure JSON.

### Safety

This preview applies basic secret-like redaction and avoids including full raw traces by default.
It does not call the GitHub API or require a GitHub token.
Review generated comments before posting to public PRs, especially if diagnosis reports may contain
proprietary logs, internal URLs, model names, or provider configuration details.

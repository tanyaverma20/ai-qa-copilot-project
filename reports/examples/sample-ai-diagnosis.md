# AI Diagnosis Report

## Summary

The example artifact set shows five common QA failure modes: API status mismatch, Playwright visibility failure, API contract mismatch, flaky UI timing, and fixture/setup failure.

## Failure Mode Matrix

| Failure Mode | Affected Test / Artifact | Evidence | Likely Classification | Next Action |
| --- | --- | --- | --- | --- |
| Product/API behavior | `tests/api/test_orders_api.py::test_create_order_rejects_insufficient_stock` / `sample-failure.json` | Expected `409`, received `500` | Product bug | Map insufficient-stock domain errors to HTTP `409`. |
| API contract | `tests/api/test_orders_api.py::test_create_order_contract` / `api-contract-failure.json` | `POST /api/orders` returned `422`; response says `quantity` is missing | Product bug or test contract drift | Compare request body, validation schema, and expected response contract. |
| UI/E2E behavior | `tests/e2e/test_checkout_flow.py::test_checkout_button_enables_payment` / `playwright-visibility-failure.json` | `Pay now` button expected visible but was hidden | Product bug or UI readiness bug | Inspect checkout state, screenshot, and trace around the hidden button. |
| Flaky/timing | `tests/e2e/test_product_search.py::test_search_filters_results` / `flaky-search-failure.json` | Passed 7 times and failed 3 times over 10 CI runs | Flaky test | Wait on stable search results instead of racing debounce and fetch state. |
| Environment/setup | `tests/conftest.py::db_seed_fixture` / `fixture-setup-failure.json` | `sqlite3.OperationalError: no such table: products` during setup | Environment issue | Ensure database initialization runs before seed fixtures touch `products`. |

## Suspected root cause

- `sample-failure.json`: the order API likely lets a stock validation exception escape as HTTP `500` instead of mapping it to HTTP `409`.
- `playwright-visibility-failure.json`: the checkout flow likely leaves the `Pay now` button hidden because a required UI state or async payment readiness signal did not complete.
- `api-contract-failure.json`: the order creation request/response contract drifted; the API returned validation errors where the test expected a created order payload.
- `flaky-search-failure.json`: the search assertion likely races product fetch or debounce behavior, producing inconsistent result counts across runs.
- `fixture-setup-failure.json`: database initialization did not finish before the seed fixture tried to insert or query product rows.

## Reproduction steps

1. Generate the demo prompt from `reports/examples`.
2. Review each artifact's `nodeid`, `phase`, `keywords`, and `longrepr`.
3. Re-run the failing test node when it points to a real test.
4. For Playwright failures, inspect the referenced screenshot and trace.

## Evidence

The artifacts include status-code mismatches, locator visibility output, request/response snippets, flaky pass/fail history, and setup exception text.

## Suggested fix

- Map domain errors to explicit API responses.
- Add UI readiness checks around checkout state transitions.
- Keep API tests aligned with the public request/response schema.
- Make flaky UI assertions wait on stable app state instead of transient counts.
- Ensure database initialization runs before seed fixtures.

## Risk level

Medium

## Classification

Mixed: product bug, test script bug, and environment issue

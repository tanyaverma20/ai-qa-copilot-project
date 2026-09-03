# Regression Test & QA Dashboard

## Purpose & Workflow

The QA Dashboard consolidates stored requirement traceability records, test case execution statuses, and defect references into a centralized QA regression dashboard.

```text
Software Requirement / User Story
             │
             ▼
   AI Test Case Generation (/test-case-generator)
             │
             ▼
   Traceability Matrix Persistence (/traceability)
             │
             ▼
   Execution & Defect Tracking
             │
             ▼
   Regression Validation & QA Dashboard (/qa-dashboard)
```

---

## Data Sources & Integrity

- **Zero Fabricated Metrics**: All metrics, counts, pass rates, defect references, and regression lists are calculated dynamically from real stored SQLite records (`traceability_requirements` and `traceability_test_cases`).
- **Global Metric Constancy**: Summary metrics reflect the entire stored dataset across all requirements. Active list filters alter only the displayed test case tables, keeping top-level KPI metrics consistent.

---

## Metric Calculations

| Metric | Formula / Source |
| --- | --- |
| **Total Requirements** | Count of unique requirement records stored. |
| **Total Test Cases** | Count of total test cases stored across all requirements. |
| **Executed Test Cases** | `Passed + Failed + Blocked + Retest` |
| **Passed / Failed / Blocked / Retest / Not Run** | Dynamic counts matching corresponding `execution_status`. |
| **Pass Rate** | $\text{Pass Rate} = \frac{\text{Passed}}{\text{Passed} + \text{Failed} + \text{Blocked} + \text{Retest}} \times 100\%$<br>*(Note: `Not Run` is strictly excluded from the denominator. Returns `0.0%` when zero test cases have been executed).* |
| **Defect Count** | Count of test cases with a non-empty `defect_reference`. |
| **Regression Count** | Count of test cases where `test_type == 'Regression'`. |

---

## REST API Reference

### `GET /api/qa-dashboard`

Returns structured QA dashboard summary metrics, defect-linked test cases, regression test cases, and filtered test cases.

- **Query Parameters (Optional)**:
  - `status`: Filter displayed test cases by `execution_status` (`Not Run`, `Passed`, `Failed`, `Blocked`, `Retest`).
  - `priority`: Filter by `priority` (`High`, `Medium`, `Low`).
  - `test_type`: Filter by `test_type` (`Regression`, `Functional`, `Negative`, `Boundary`).
  - `requirement_id`: Partial substring filter for `requirement_id`.

- **Sample Response**: `200 OK`
  ```json
  {
    "summary": {
      "total_requirements": 5,
      "total_test_cases": 18,
      "executed_test_cases": 12,
      "passed": 9,
      "failed": 2,
      "blocked": 1,
      "retest": 0,
      "not_run": 6,
      "pass_rate": 75.0,
      "defect_count": 2,
      "regression_count": 4
    },
    "defect_cases": [...],
    "regression_cases": [...],
    "test_cases": [...]
  }
  ```

---

## UI Guide (`/qa-dashboard`)

1. **Header Cards**: Displays high-level KPIs including Pass Rate %, Total Requirements, Total Test Cases, and Regression Count.
2. **Defect Visibility**: Highlights all test cases marked as `Failed`, `Blocked`, `Retest`, or linked with a defect ID.
3. **Regression Filter Table**: Filter test cases by Execution Status, Priority, Test Type, or Requirement ID, with distinct `[REGRESSION]` badges highlighting regression tests.

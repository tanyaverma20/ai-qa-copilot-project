# Requirement-to-Test-Case Traceability

## Overview

Requirement-to-Test-Case Traceability establishes a bidirectional link between software requirements (User Stories) and the QA test cases generated to validate them. In AI QA Copilot, this feature tracks the lifecycle of each requirement from initial test case generation to execution, result recording, and defect linkage.

---

## Data Flow

```text
Software Requirement / User Story
             │
             ▼
   AI Test Case Generator (/test-case-generator)
             │
             ▼
   Save to Traceability Matrix (POST /api/traceability)
             │
             ▼
   SQLite Database (traceability_requirements & traceability_test_cases)
             │
             ▼
   Traceability Matrix UI (/traceability)
             │
             ▼
   Update Status / Actual Result / Defect Ref (PATCH /api/traceability/...)
```

---

## Execution Status Meanings

| Execution Status | Meaning / Purpose |
| --- | --- |
| **Not Run** | Test case has been generated and linked, but has not yet been executed. |
| **Passed** | Test execution succeeded; actual behavior matched expected results cleanly. |
| **Failed** | Test execution failed; actual behavior diverged from expected criteria. |
| **Blocked** | Test execution is currently blocked by environmental issues or dependency failures. |
| **Retest** | Test case needs re-execution following a defect fix or environment update. |

---

## REST API Reference

### 1. `POST /api/traceability`
Saves or idempotently updates a requirement and its linked test cases.

- **Request Body**:
  ```json
  {
    "requirement_id": "REQ-SHOP-01",
    "user_story": "As a customer, I want to add items to my cart.",
    "test_cases": [
      {
        "test_case_id": "TC-001",
        "requirement_id": "REQ-SHOP-01",
        "scenario": "Verify valid product can be added to cart",
        "preconditions": ["User is logged in"],
        "test_steps": ["Click Add to Cart"],
        "expected_result": "Product added to cart",
        "test_type": "Functional",
        "priority": "High"
      }
    ]
  }
  ```
- **Response**: `201 Created` with full saved requirement record.

---

### 2. `GET /api/traceability`
Lists all saved requirements, linked test cases, and aggregate summary metrics.

- **Response**: `200 OK`
  ```json
  {
    "records": [...],
    "summary": {
      "total_requirements": 1,
      "total_test_cases": 1,
      "passed": 0,
      "failed": 0,
      "blocked": 0,
      "not_run": 1,
      "retest": 0
    }
  }
  ```

---

### 3. `GET /api/traceability/{requirement_id}`
Retrieves traceability record for a specific Requirement ID.

- **Response**: `200 OK` (or `404 Not Found` if requirement does not exist).

---

### 4. `PATCH /api/traceability/{requirement_id}/test-cases/{test_case_id}`
Updates execution status, actual result, or defect reference for a linked test case.

- **Request Body**:
  ```json
  {
    "execution_status": "Failed",
    "actual_result": "Error alert displayed: Stock mismatch",
    "defect_reference": "DEFECT-101"
  }
  ```
- **Response**: `200 OK` with updated test case object (or `422 Unprocessable Entity` for invalid execution status).

---

## UI Guide

1. Navigate to `/test-case-generator`.
2. Input Requirement ID and User Story text -> click **生成结构化测试用例**.
3. Once generated, click **保存至 Traceability 追溯矩阵**.
4. Navigate to `/traceability` to view the requirement and its linked test cases.
5. Update execution status, input actual results, or add defect references -> click **保存** to update the database.

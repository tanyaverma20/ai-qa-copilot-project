# AI-Assisted Test Case Generator

The **AI-Assisted Test Case Generator** transforms software requirements or user stories into structured QA test case suites using the platform's multi-provider LLM abstraction layer.

---

## Key Features

1. **Structured QA Output**:
   - **Test Case ID**: Standardized identifier (e.g. `TC-001`).
   - **Requirement ID**: Traced requirement identifier (e.g. `REQ-001`).
   - **Scenario**: Concise description of the test scenario.
   - **Preconditions**: List of required initial conditions.
   - **Test Steps**: Ordered list of execution steps.
   - **Expected Result**: Clear pass/fail assertion criteria.
   - **Test Type**: Categorized as `Functional`, `Negative`, `Boundary`, or `Regression`.
   - **Priority**: Ranked as `High`, `Medium`, or `Low`.

2. **Provider Abstraction & Fallbacks**:
   - Leverages `qa_copilot.providers` (`DiagnosisProviderConfig`, `create_diagnosis_provider`).
   - Reuses existing provider configuration (`AI_PROVIDER`, `OPENAI_API_KEY`, `DEEPSEEK_API_KEY`, etc.).
   - Gracefully handles unconfigured providers, missing API keys, and LLM API errors with structured error payloads.

3. **Input Validation**:
   - Rejects empty or whitespace-only inputs with clear HTTP 400 validation responses.

---

## API Reference

### Generate Test Cases
`POST /api/generate-test-cases`

**Request Body**:
```json
{
  "user_story": "As a registered user, I want to log in with my username and password so I can access the shop.",
  "requirement_id": "REQ-AUTH-01"
}
```

**Response (Success)**:
```json
{
  "ok": true,
  "requirement_id": "REQ-AUTH-01",
  "test_cases": [
    {
      "test_case_id": "TC-001",
      "requirement_id": "REQ-AUTH-01",
      "scenario": "Successful login with valid credentials",
      "preconditions": ["User account is active"],
      "test_steps": [
        "Navigate to /login page",
        "Enter valid username and password",
        "Click Submit"
      ],
      "expected_result": "User is redirected to /products and receives auth token",
      "test_type": "Functional",
      "priority": "High"
    },
    {
      "test_case_id": "TC-002",
      "requirement_id": "REQ-AUTH-01",
      "scenario": "Login attempt with incorrect password",
      "preconditions": ["User account exists"],
      "test_steps": [
        "Navigate to /login page",
        "Enter username and incorrect password",
        "Click Submit"
      ],
      "expected_result": "HTTP 401 Unauthorized status returned with error message",
      "test_type": "Negative",
      "priority": "High"
    }
  ],
  "error": null
}
```

**Response (Provider Unconfigured / Failed)**:
```json
{
  "ok": false,
  "requirement_id": "REQ-AUTH-01",
  "test_cases": [],
  "error": "AI provider API key is not configured."
}
```

---

## Web Interface

Access the interactive web generator at:
`http://localhost:8000/test-case-generator`

- Input requirement description and optional Requirement ID.
- Click **"生成结构化测试用例"** to trigger AI generation.
- View test case cards categorized by type and priority badges.

---

## Automated Test Coverage

The test suite includes dedicated mocked tests:
- `tests/unit/test_test_case_generator.py`: Prompt building, JSON response parsing, input validation, provider failure mocking.
- `tests/api/test_test_case_generator_api.py`: FastAPI endpoint tests (`POST /api/generate-test-cases` and `GET /test-case-generator`).

# AI-QA Copilot

AI-assisted Quality Engineering platform that combines automated API and end-to-end testing with LLM-powered test case generation, requirement-to-test-case traceability, regression analysis, and AI-assisted failure diagnosis.

The project is designed to support the complete QA workflow — from understanding requirements and generating test cases to executing tests, tracking results, identifying regressions, and diagnosing failures.

---

## Overview

AI-QA Copilot is a quality engineering platform built around the idea of combining traditional software testing with AI-assisted QA workflows.

The platform provides:

- AI-powered test case generation from requirements
- Requirement-to-test-case traceability
- Automated API testing
- Automated end-to-end testing
- Regression test tracking
- QA metrics and dashboards
- Defect and failure visibility
- AI-assisted failure diagnosis
- Automated test execution through CI/CD

The goal is to make QA workflows more structured, traceable, and efficient while keeping test execution and validation grounded in actual application behavior.

---

## Key Capabilities

### 1. AI Test Case Generator

The platform can generate structured test cases from a natural-language requirement or user story.

A requirement can be converted into test scenarios covering areas such as:

- Functional testing
- Negative testing
- Boundary testing
- Regression testing
- Different priority levels

Generated test cases contain structured information such as:

- Test case ID
- Scenario
- Test type
- Priority
- Preconditions
- Test steps
- Expected result

The generated test cases can then be saved directly into the traceability matrix for further execution and tracking.

---

### 2. Requirement-to-Test-Case Traceability

The Traceability Matrix connects requirements with their corresponding test cases.

Each requirement can be associated with multiple test cases, allowing QA teams to track:

- Requirement ID
- User story
- Test case ID
- Test scenario
- Test type
- Priority
- Execution status
- Actual result
- Defect reference

Supported execution statuses include:

- Not Run
- Passed
- Failed
- Blocked
- Retest

The system uses persistent SQLite storage so that test execution information is retained between sessions.

The traceability workflow helps establish a clear relationship:

```text
Requirement
     ↓
Test Case
     ↓
Execution Result
     ↓
Defect / Retest
```

---

### 3. Regression Test & QA Dashboard

The QA Dashboard provides a centralized view of testing progress and quality status.

The dashboard calculates metrics directly from stored traceability data, including:

- Total requirements
- Total test cases
- Executed test cases
- Passed tests
- Failed tests
- Blocked tests
- Retest cases
- Not-run tests
- Pass rate
- Defect count
- Regression test count

The dashboard also supports filtering test cases by:

- Status
- Priority
- Test type
- Requirement ID

The pass rate is calculated only from executed test cases, excluding tests that have not yet been run:

$$\text{Pass Rate} = \frac{\text{Passed}}{\text{Passed} + \text{Failed} + \text{Blocked} + \text{Retest}} \times 100\%$$

This provides a more meaningful view of current QA execution status.

---

### 4. AI-Assisted Failure Diagnosis

The platform can analyze failed automated tests and generate an AI-assisted diagnosis.

The diagnosis workflow uses available test failure evidence to identify:

- Failure classification
- Possible root cause
- Candidate explanation
- Recommended next action

Failure evidence can include:

- Test output
- Error messages
- Screenshots
- Traces
- JSON reports
- HTML reports

The purpose is not to replace QA engineers, but to reduce the time required to understand and investigate automated test failures.

---

### 5. Automated API Testing

The project includes automated API and service-level testing for the FastAPI application.

The API test suite validates:

- API behavior
- Request validation
- Response validation
- Error handling
- Service workflows
- API contracts

The test suite is integrated into the project's QA workflow and can be executed locally or through CI.

---

### 6. End-to-End Testing

The project uses browser-based end-to-end testing to validate complete application workflows.

E2E testing helps verify that multiple application components work together correctly from the user's perspective.

The workflow includes:

```text
Application
    ↓
Browser Interaction
    ↓
User Workflow
    ↓
Expected Result
```

Failure evidence such as screenshots and traces can be used during failure investigation.

---

## QA Workflow

The overall workflow of the platform is:

```text
                 Requirement / User Story
                           │
                           ▼
                AI Test Case Generator
                           │
                           ▼
                 Traceability Matrix
                           │
                           ▼
              API & E2E Test Execution
                           │
                           ▼
                 Regression Validation
                           │
                           ▼
                 QA Metrics Dashboard
                           │
                           ▼
                Failure / Defect Analysis
                           │
                           ▼
                 AI Failure Diagnosis
```

This creates a connected QA lifecycle rather than treating test generation, execution, and reporting as separate activities.

---

## Architecture

```text
┌──────────────────────────────┐
│      Requirement / Story     │
└──────────────┬───────────────┘
               │
               ▼
┌──────────────────────────────┐
│     AI Test Case Generator   │
│                              │
│ Requirement → Test Cases     │
└──────────────┬───────────────┘
               │
               ▼
┌──────────────────────────────┐
│    Traceability Matrix       │
│                              │
│ Requirement → Test Case      │
│ Test Case → Execution        │
│ Execution → Defect           │
└──────────────┬───────────────┘
               │
               ▼
┌──────────────────────────────┐
│      Test Execution          │
│                              │
│      pytest + Playwright     │
└──────────────┬───────────────┘
               │
               ▼
┌──────────────────────────────┐
│    Regression & QA Dashboard │
│                              │
│ Metrics • Status • Defects   │
└──────────────┬───────────────┘
               │
               ▼
┌──────────────────────────────┐
│    AI Failure Diagnosis      │
│                              │
│ Evidence → Diagnosis         │
└──────────────────────────────┘
```

---

## Technology Stack

### Backend
- Python
- FastAPI
- Pydantic
- SQLite

### AI / LLM
- LLM provider abstraction
- Structured LLM output handling
- AI-assisted test case generation
- AI-assisted failure diagnosis

### Testing
- pytest
- Playwright
- API testing
- End-to-end testing
- Regression testing

### Frontend
- HTML
- CSS
- JavaScript

### Development & CI
- Git
- GitHub
- GitHub Actions
- Ruff

---

## Project Structure

```text
ai-qa-copilot-project/
│
├── .github/
│   └── workflows/
│       └── ...
│
├── app/
│   ├── main.py
│   ├── db.py
│   ├── schemas.py
│   ├── templates/
│   │   ├── ...
│   │   ├── test_case_generator.html
│   │   ├── traceability.html
│   │   └── qa_dashboard.html
│   └── ...
│
├── qa_copilot/
│   ├── test_case_generator.py
│   ├── traceability.py
│   ├── qa_dashboard.py
│   └── ...
│
├── tests/
│   ├── api/
│   │   ├── ...
│   │   ├── test_test_case_generator_api.py
│   │   ├── test_traceability_api.py
│   │   └── test_qa_dashboard_api.py
│   │
│   └── unit/
│       ├── ...
│       ├── test_test_case_generator.py
│       ├── test_traceability.py
│       └── test_qa_dashboard.py
│
├── docs/
│   ├── test-case-generator.md
│   ├── traceability.md
│   ├── qa-dashboard.md
│   └── ...
│
├── reports/
│   └── examples/
│
├── scripts/
│   └── ...
│
├── .gitignore
├── README.md
└── ...
```

---

## Test Case Generation Workflow

The AI Test Case Generator follows a structured process:

```text
User Requirement
       │
       ▼
Input Validation
       │
       ▼
LLM Prompt Construction
       │
       ▼
LLM Provider
       │
       ▼
Structured JSON Response
       │
       ▼
Validation & Parsing
       │
       ▼
Structured Test Cases
       │
       ▼
Traceability Matrix
```

The implementation includes validation for generated test-case data and handles both raw JSON responses and JSON contained inside Markdown code blocks.

---

## Traceability Workflow

Test cases generated from requirements can be persisted in the traceability system.

The traceability system provides:

```text
Requirement
     │
     ├── Test Case 1
     │      └── Execution Status
     │
     ├── Test Case 2
     │      └── Execution Status
     │
     └── Test Case 3
            ├── Execution Status
            └── Defect Reference
```

The database layer also enforces foreign-key relationships to maintain data consistency.

Idempotent save behavior prevents accidental duplication when the same test case is saved multiple times.

---

## QA Dashboard

The dashboard provides a centralized view of the current testing state.

Example metrics include:

- Total Test Cases
- Executed Test Cases
- Passed
- Failed
- Blocked
- Retest
- Not Run
- Pass Rate
- Defects
- Regression Tests

Global metrics are calculated using the complete stored dataset, while filters are applied to the displayed test-case list.

This ensures that filtering the dashboard does not incorrectly change the overall project-level QA metrics.

---

## API Endpoints

### Test Case Generator
- `POST /api/generate-test-cases`: Generates structured test cases from a requirement.
- `GET /test-case-generator`: Opens the Test Case Generator interface.

### Traceability
- `POST /api/traceability`: Creates or updates a requirement and its test cases.
- `GET /api/traceability`: Returns traceability data.
- `GET /api/traceability/{requirement_id}`: Returns test cases associated with a specific requirement.
- `PATCH /api/traceability/{requirement_id}/test-cases/{test_case_id}`: Updates execution information for a test case.
- `GET /traceability`: Opens the Traceability Matrix interface.

### QA Dashboard
- `GET /api/qa-dashboard`: Returns QA metrics and filtered test-case information.
- `GET /qa-dashboard`: Opens the QA Dashboard.

---

## Running the Project

### 1. Clone the repository
```powershell
git clone https://github.com/tanyaverma20/ai-qa-copilot-project.git
cd ai-qa-copilot-project
```

### 2. Create a virtual environment
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies
```powershell
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
python -m playwright install chromium
```

### 4. Configure environment variables
Create a local `.env` file based on the project's environment configuration. Do not commit API keys or other secrets.

### 5. Start the Application
```powershell
uvicorn app.main:app --reload
```

Then open the application in the browser at `http://127.0.0.1:8000`.

The main QA modules include:
- `/test-case-generator`
- `/traceability`
- `/qa-dashboard`

---

## Running Tests

Run the complete automated test suite:

```powershell
python -m pytest -v
```

The project currently contains 150 automated tests, covering the application's API, business logic, test-case generation, traceability, and QA dashboard functionality.

Latest verification: **150 passed**.

---

## Code Quality

Ruff is used for static code-quality checks:

```powershell
ruff check .
```

Run full local verification:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/verify.ps1
```

---

## Continuous Integration

GitHub Actions is used to automate project validation:

```text
Code Quality
     ↓
Automated Tests
     ↓
Test Reports
     ↓
Build / Verification
```

---

## Quality Engineering Principles

- **Requirement Traceability**: Every test should be connected to a requirement or user story wherever applicable.
- **Early Validation**: Requirements and test scenarios should be validated before relying on implementation-level testing.
- **Automation**: Repeated API, regression, and end-to-end checks should be automated wherever practical.
- **Evidence-Based Diagnosis**: Test failures should be analyzed using actual failure evidence rather than assumptions.
- **Regression Protection**: Existing functionality should be continuously checked after changes to reduce regression risk.
- **Clear Defect Tracking**: Failed and blocked tests can contain defect references to make failures easier to follow up.
- **Data Consistency**: Persistent traceability information uses database constraints and validation to reduce inconsistent QA data.

---

## What This Project Demonstrates

This project demonstrates practical experience across both AI engineering and Quality Engineering, including:

- AI/LLM-assisted software testing
- Test case design (Functional, Negative, Boundary, Regression)
- API testing & End-to-end testing
- Test execution tracking & Requirement traceability
- Defect visibility & Failure analysis
- SQL/database persistence & REST API development
- Automated testing & CI/CD validation
- AI-assisted developer workflows

---

## Future Enhancements

- Requirement-to-test-case coverage reports
- Automated defect creation and integration with issue trackers
- More advanced AI root-cause analysis
- Test-case prioritization using risk-based scoring
- Additional API contract testing
- Historical QA trend analysis
- Test execution scheduling
- Integration with external test management systems
- Enhanced regression analytics

---

## Author

**Tanya Verma**  
B.Tech Computer Engineering  
Thapar Institute of Engineering and Technology  

- **GitHub:** [https://github.com/tanyaverma20](https://github.com/tanyaverma20)
- **Project Focus:** AI + Quality Engineering + Test Automation + Backend Development

*The project focuses on using AI to assist—not replace—traditional software quality practices by connecting requirements, test design, automated execution, regression validation, and failure diagnosis into one workflow.*

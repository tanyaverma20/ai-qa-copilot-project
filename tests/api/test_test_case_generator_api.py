from __future__ import annotations

from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import create_app
from qa_copilot.test_case_generator import TestCase, TestCaseGenerationResult


def test_api_generate_test_cases_valid_input() -> None:
    app = create_app(":memory:")
    client = TestClient(app)

    mock_result = TestCaseGenerationResult(
        ok=True,
        requirement_id="REQ-API-001",
        test_cases=[
            TestCase(
                test_case_id="TC-001",
                requirement_id="REQ-API-001",
                scenario="Successful user login",
                preconditions=["User account exists"],
                test_steps=["Submit valid credentials"],
                expected_result="Access token returned",
                test_type="Functional",
                priority="High",
            ),
            TestCase(
                test_case_id="TC-002",
                requirement_id="REQ-API-001",
                scenario="Login with invalid password",
                preconditions=["User account exists"],
                test_steps=["Submit invalid password"],
                expected_result="401 Unauthorized returned",
                test_type="Negative",
                priority="High",
            ),
        ],
    )

    with patch(
        "app.main.generate_test_cases",
        return_value=mock_result,
    ) as mock_gen:
        response = client.post(
            "/api/generate-test-cases",
            json={
                "user_story": "As a user, I want to log in with username and password.",
                "requirement_id": "REQ-API-001",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["ok"] is True
        assert data["requirement_id"] == "REQ-API-001"
        assert len(data["test_cases"]) == 2
        assert data["test_cases"][0]["test_case_id"] == "TC-001"
        assert data["test_cases"][1]["test_type"] == "Negative"
        mock_gen.assert_called_once()


def test_api_generate_test_cases_empty_input() -> None:
    app = create_app(":memory:")
    client = TestClient(app)

    response = client.post(
        "/api/generate-test-cases",
        json={"user_story": "   ", "requirement_id": "REQ-001"},
    )

    assert response.status_code == 400
    data = response.json()
    assert "cannot be empty" in data["detail"]


def test_api_generate_test_cases_provider_failure() -> None:
    app = create_app(":memory:")
    client = TestClient(app)

    mock_failed_result = TestCaseGenerationResult(
        ok=False,
        requirement_id="REQ-FAIL-01",
        test_cases=[],
        error="AI provider API key is not configured.",
    )

    with patch("app.main.generate_test_cases", return_value=mock_failed_result):
        response = client.post(
            "/api/generate-test-cases",
            json={
                "user_story": "As a user, I want to checkout my cart.",
                "requirement_id": "REQ-FAIL-01",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["ok"] is False
        assert data["requirement_id"] == "REQ-FAIL-01"
        assert data["test_cases"] == []
        assert "not configured" in data["error"]


def test_get_test_case_generator_page() -> None:
    app = create_app(":memory:")
    client = TestClient(app)

    response = client.get("/test-case-generator")
    assert response.status_code == 200
    assert "AI 辅助测试用例生成器" in response.text
    assert "generateTestCases()" in response.text

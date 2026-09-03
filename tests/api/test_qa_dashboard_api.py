from __future__ import annotations

from fastapi.testclient import TestClient


def test_get_qa_dashboard_api_empty_db(client: TestClient) -> None:
    res = client.get("/api/qa-dashboard")
    assert res.status_code == 200
    data = res.json()

    assert "summary" in data
    assert data["summary"]["total_requirements"] == 0
    assert data["summary"]["total_test_cases"] == 0
    assert data["summary"]["pass_rate"] == 0.0
    assert data["defect_cases"] == []
    assert data["regression_cases"] == []
    assert data["test_cases"] == []


def test_get_qa_dashboard_api_with_data_and_filters(client: TestClient) -> None:
    # 1. Create traceability record via API
    client.post(
        "/api/traceability",
        json={
            "requirement_id": "REQ-DASH-01",
            "user_story": "As a QA lead, I want a dashboard API.",
            "test_cases": [
                {
                    "test_case_id": "TC-DASH-101",
                    "requirement_id": "REQ-DASH-01",
                    "scenario": "Verify dashboard summary",
                    "expected_result": "Summary rendered",
                    "test_type": "Regression",
                    "priority": "High",
                },
                {
                    "test_case_id": "TC-DASH-102",
                    "requirement_id": "REQ-DASH-01",
                    "scenario": "Verify dashboard defect list",
                    "expected_result": "Defects rendered",
                    "test_type": "Functional",
                    "priority": "Medium",
                },
            ],
        },
    )

    # Update TC-DASH-101 to Passed, TC-DASH-102 to Failed with defect ref
    client.patch(
        "/api/traceability/REQ-DASH-01/test-cases/TC-DASH-101",
        json={"execution_status": "Passed"},
    )
    client.patch(
        "/api/traceability/REQ-DASH-01/test-cases/TC-DASH-102",
        json={"execution_status": "Failed", "defect_reference": "DEF-900"},
    )

    # 2. Fetch unfiltered dashboard API
    res = client.get("/api/qa-dashboard")
    assert res.status_code == 200
    data = res.json()
    summary = data["summary"]

    assert summary["total_requirements"] == 1
    assert summary["total_test_cases"] == 2
    assert summary["executed_test_cases"] == 2
    assert summary["passed"] == 1
    assert summary["failed"] == 1
    assert summary["pass_rate"] == 50.0
    assert summary["defect_count"] == 1
    assert summary["regression_count"] == 1

    assert len(data["regression_cases"]) == 1
    assert data["regression_cases"][0]["test_case_id"] == "TC-DASH-101"

    assert len(data["defect_cases"]) == 1
    assert data["defect_cases"][0]["test_case_id"] == "TC-DASH-102"
    assert data["defect_cases"][0]["defect_reference"] == "DEF-900"

    # 3. Fetch filtered dashboard API
    res_filt = client.get("/api/qa-dashboard?test_type=Regression")
    assert res_filt.status_code == 200
    data_filt = res_filt.json()

    # Summary stays global and unchanged
    assert data_filt["summary"] == summary

    # Displayed test cases filtered to only Regression
    assert len(data_filt["test_cases"]) == 1
    assert data_filt["test_cases"][0]["test_case_id"] == "TC-DASH-101"


def test_qa_dashboard_ui_page_returns_200(client: TestClient) -> None:
    res = client.get("/qa-dashboard")
    assert res.status_code == 200
    assert "回归测试与 QA 综合看板" in res.text
    assert "QA Dashboard" in res.text
    assert "总体通过率 (Pass Rate)" in res.text
    assert "缺陷与异常暴露视图" in res.text
    assert "回归测试用例明细" in res.text

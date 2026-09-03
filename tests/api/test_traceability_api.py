from __future__ import annotations

from fastapi.testclient import TestClient


def test_create_and_retrieve_traceability_record(client: TestClient) -> None:
    payload = {
        "requirement_id": "REQ-API-01",
        "user_story": "As an API client, I want to create traceability records.",
        "test_cases": [
            {
                "test_case_id": "TC-API-101",
                "requirement_id": "REQ-API-01",
                "scenario": "Post valid traceability payload",
                "preconditions": ["API server is running"],
                "test_steps": ["Send POST /api/traceability"],
                "expected_result": "201 Created status returned",
                "test_type": "Functional",
                "priority": "High",
            }
        ],
    }

    # 1. Post record
    res_create = client.post("/api/traceability", json=payload)
    assert res_create.status_code == 201
    data_create = res_create.json()
    assert data_create["requirement_id"] == "REQ-API-01"
    assert len(data_create["test_cases"]) == 1
    assert data_create["test_cases"][0]["execution_status"] == "Not Run"

    # 2. Get specific record
    res_get = client.get("/api/traceability/REQ-API-01")
    assert res_get.status_code == 200
    data_get = res_get.json()
    assert data_get["requirement_id"] == "REQ-API-01"
    assert data_get["user_story"] == "As an API client, I want to create traceability records."
    assert data_get["test_cases"][0]["test_case_id"] == "TC-API-101"


def test_list_traceability_records_and_summary(client: TestClient) -> None:
    client.post(
        "/api/traceability",
        json={
            "requirement_id": "REQ-LIST-01",
            "user_story": "Requirement for listing test",
            "test_cases": [
                {
                    "test_case_id": "TC-LIST-01",
                    "requirement_id": "REQ-LIST-01",
                    "scenario": "Listing scenario",
                    "expected_result": "Success",
                    "test_type": "Functional",
                    "priority": "Medium",
                }
            ],
        },
    )

    res = client.get("/api/traceability")
    assert res.status_code == 200
    data = res.json()
    assert "records" in data
    assert "summary" in data
    assert data["summary"]["total_requirements"] >= 1
    assert data["summary"]["total_test_cases"] >= 1


def test_update_traceability_test_case_and_verify_persistence(client: TestClient) -> None:
    # Create initial record
    client.post(
        "/api/traceability",
        json={
            "requirement_id": "REQ-PERSIST-01",
            "user_story": "Test persistence of execution updates",
            "test_cases": [
                {
                    "test_case_id": "TC-PER-01",
                    "requirement_id": "REQ-PERSIST-01",
                    "scenario": "Persistence test scenario",
                    "expected_result": "Initial expected result",
                    "test_type": "Functional",
                    "priority": "High",
                }
            ],
        },
    )

    # Patch update
    res_patch = client.patch(
        "/api/traceability/REQ-PERSIST-01/test-cases/TC-PER-01",
        json={
            "execution_status": "Failed",
            "actual_result": "Element #submit-btn not visible within 5s",
            "defect_reference": "DEFECT-BUG-909",
        },
    )
    assert res_patch.status_code == 200
    data_patch = res_patch.json()
    assert data_patch["execution_status"] == "Failed"
    assert data_patch["actual_result"] == "Element #submit-btn not visible within 5s"
    assert data_patch["defect_reference"] == "DEFECT-BUG-909"

    # Retrieve record and confirm persistent values in DB
    res_get = client.get("/api/traceability/REQ-PERSIST-01")
    assert res_get.status_code == 200
    tc_retrieved = res_get.json()["test_cases"][0]
    assert tc_retrieved["execution_status"] == "Failed"
    assert tc_retrieved["actual_result"] == "Element #submit-btn not visible within 5s"
    assert tc_retrieved["defect_reference"] == "DEFECT-BUG-909"


def test_invalid_execution_status_returns_422(client: TestClient) -> None:
    # Create initial record
    client.post(
        "/api/traceability",
        json={
            "requirement_id": "REQ-VAL-01",
            "user_story": "Validation test requirement",
            "test_cases": [
                {
                    "test_case_id": "TC-VAL-01",
                    "requirement_id": "REQ-VAL-01",
                    "scenario": "Validation scenario",
                    "expected_result": "Expected",
                    "test_type": "Functional",
                    "priority": "Medium",
                }
            ],
        },
    )

    # Attempt patch with invalid execution status
    res_patch = client.patch(
        "/api/traceability/REQ-VAL-01/test-cases/TC-VAL-01",
        json={"execution_status": "InvalidStatusXYZ"},
    )
    assert res_patch.status_code == 422  # Unprocessable Entity from Pydantic validation


def test_missing_requirement_returns_404(client: TestClient) -> None:
    res_get = client.get("/api/traceability/NONEXISTENT-REQ-ID")
    assert res_get.status_code == 404
    assert "not found" in res_get.json()["detail"].lower()


def test_update_missing_test_case_returns_404(client: TestClient) -> None:
    client.post(
        "/api/traceability",
        json={
            "requirement_id": "REQ-EXIST-01",
            "user_story": "Existing requirement",
            "test_cases": [
                {
                    "test_case_id": "TC-EXIST-01",
                    "requirement_id": "REQ-EXIST-01",
                    "scenario": "Scenario",
                    "expected_result": "Result",
                    "test_type": "Functional",
                    "priority": "Low",
                }
            ],
        },
    )

    res_patch = client.patch(
        "/api/traceability/REQ-EXIST-01/test-cases/TC-MISSING-99",
        json={"execution_status": "Passed"},
    )
    assert res_patch.status_code == 404


def test_traceability_ui_page_returns_200(client: TestClient) -> None:
    res = client.get("/traceability")
    assert res.status_code == 200
    assert "需求与测试用例追溯矩阵" in res.text
    assert "Traceability" in res.text

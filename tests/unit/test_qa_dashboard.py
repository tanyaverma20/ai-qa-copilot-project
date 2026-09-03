from __future__ import annotations

import sqlite3

import pytest

from app.db import connect, initialize_database
from qa_copilot.qa_dashboard import get_qa_dashboard_data
from qa_copilot.traceability import save_traceability_record, update_traceability_test_case


@pytest.fixture
def db_conn() -> sqlite3.Connection:
    conn = connect(":memory:")
    initialize_database(conn)
    return conn


def test_empty_database_qa_dashboard(db_conn: sqlite3.Connection) -> None:
    data = get_qa_dashboard_data(db_conn)
    summary = data["summary"]

    assert summary["total_requirements"] == 0
    assert summary["total_test_cases"] == 0
    assert summary["executed_test_cases"] == 0
    assert summary["passed"] == 0
    assert summary["failed"] == 0
    assert summary["blocked"] == 0
    assert summary["retest"] == 0
    assert summary["not_run"] == 0
    assert summary["pass_rate"] == 0.0
    assert summary["defect_count"] == 0
    assert summary["regression_count"] == 0
    assert data["test_cases"] == []
    assert data["defect_cases"] == []
    assert data["regression_cases"] == []


def test_zero_executed_test_cases_pass_rate(db_conn: sqlite3.Connection) -> None:
    # Save requirement with 3 test cases, all 'Not Run'
    save_traceability_record(
        db_conn,
        requirement_id="REQ-ZERO-01",
        user_story="Zero execution test story",
        test_cases=[
            {
                "test_case_id": "TC-Z1",
                "scenario": "Scenario Z1",
                "test_type": "Functional",
                "priority": "High",
                "expected_result": "Exp Z1",
            },
            {
                "test_case_id": "TC-Z2",
                "scenario": "Scenario Z2",
                "test_type": "Regression",
                "priority": "Medium",
                "expected_result": "Exp Z2",
            },
        ],
    )

    data = get_qa_dashboard_data(db_conn)
    summary = data["summary"]

    assert summary["total_test_cases"] == 2
    assert summary["executed_test_cases"] == 0
    assert summary["not_run"] == 2
    assert summary["pass_rate"] == 0.0  # Safe division-by-zero check


def test_pass_rate_calculation_excludes_not_run(db_conn: sqlite3.Connection) -> None:
    # 3 Passed, 1 Failed, 1 Blocked, 5 Not Run -> Executed = 5 -> Pass Rate = 3 / 5 * 100 = 60.0%
    test_cases = [
        {"test_case_id": f"TC-{i:02d}", "scenario": f"Scenario {i}", "expected_result": "Exp"}
        for i in range(1, 11)
    ]
    save_traceability_record(
        db_conn,
        requirement_id="REQ-MATH-01",
        user_story="Math verification story",
        test_cases=test_cases,
    )

    update_traceability_test_case(
        db_conn, "REQ-MATH-01", "TC-01", execution_status="Passed"
    )
    update_traceability_test_case(
        db_conn, "REQ-MATH-01", "TC-02", execution_status="Passed"
    )
    update_traceability_test_case(
        db_conn, "REQ-MATH-01", "TC-03", execution_status="Passed"
    )
    update_traceability_test_case(
        db_conn, "REQ-MATH-01", "TC-04", execution_status="Failed"
    )
    update_traceability_test_case(
        db_conn, "REQ-MATH-01", "TC-05", execution_status="Blocked"
    )

    data = get_qa_dashboard_data(db_conn)
    summary = data["summary"]

    assert summary["total_test_cases"] == 10
    assert summary["executed_test_cases"] == 5
    assert summary["passed"] == 3
    assert summary["failed"] == 1
    assert summary["blocked"] == 1
    assert summary["not_run"] == 5
    assert summary["pass_rate"] == 60.0


def test_filtering_does_not_change_global_summary_metrics(
    db_conn: sqlite3.Connection,
) -> None:
    save_traceability_record(
        db_conn,
        requirement_id="REQ-FILT-01",
        user_story="Filtering test story",
        test_cases=[
            {
                "test_case_id": "TC-F1",
                "scenario": "Functional Passed",
                "test_type": "Functional",
                "priority": "High",
                "expected_result": "Exp F1",
            },
            {
                "test_case_id": "TC-R1",
                "scenario": "Regression Failed",
                "test_type": "Regression",
                "priority": "Low",
                "expected_result": "Exp R1",
            },
        ],
    )
    update_traceability_test_case(
        db_conn, "REQ-FILT-01", "TC-F1", execution_status="Passed"
    )
    update_traceability_test_case(
        db_conn,
        "REQ-FILT-01",
        "TC-R1",
        execution_status="Failed",
        defect_reference="BUG-101",
    )

    unfiltered = get_qa_dashboard_data(db_conn)
    filtered = get_qa_dashboard_data(
        db_conn, status="Failed", test_type="Regression", priority="Low"
    )

    # Global summary must be identical regardless of filters
    assert filtered["summary"] == unfiltered["summary"]
    assert filtered["summary"]["total_test_cases"] == 2
    assert filtered["summary"]["pass_rate"] == 50.0

    # Displayed test_cases list MUST be filtered
    assert len(filtered["test_cases"]) == 1
    assert filtered["test_cases"][0]["test_case_id"] == "TC-R1"


def test_defect_cases_and_regression_cases_identification(
    db_conn: sqlite3.Connection,
) -> None:
    save_traceability_record(
        db_conn,
        requirement_id="REQ-DEF-01",
        user_story="Defects and regression story",
        test_cases=[
            {
                "test_case_id": "TC-REG-1",
                "scenario": "Regression pass scenario",
                "test_type": "Regression",
                "priority": "High",
                "expected_result": "Exp",
            },
            {
                "test_case_id": "TC-BUG-1",
                "scenario": "Functional failed scenario",
                "test_type": "Functional",
                "priority": "High",
                "expected_result": "Exp",
            },
        ],
    )
    update_traceability_test_case(
        db_conn, "REQ-DEF-01", "TC-REG-1", execution_status="Passed"
    )
    update_traceability_test_case(
        db_conn,
        "REQ-DEF-01",
        "TC-BUG-1",
        execution_status="Failed",
        defect_reference="ISSUE-999",
    )

    data = get_qa_dashboard_data(db_conn)

    assert len(data["regression_cases"]) == 1
    assert data["regression_cases"][0]["test_case_id"] == "TC-REG-1"

    assert len(data["defect_cases"]) == 1
    assert data["defect_cases"][0]["test_case_id"] == "TC-BUG-1"
    assert data["defect_cases"][0]["defect_reference"] == "ISSUE-999"

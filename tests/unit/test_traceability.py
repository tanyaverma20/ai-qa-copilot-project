from __future__ import annotations

import sqlite3

import pytest

from app.db import connect, initialize_database
from qa_copilot.traceability import (
    TraceabilityNotFoundError,
    TraceabilityValidationError,
    get_traceability_record,
    get_traceability_summary,
    list_traceability_records,
    save_traceability_record,
    update_traceability_test_case,
    validate_execution_status,
)


@pytest.fixture
def db_conn() -> sqlite3.Connection:
    conn = connect(":memory:")
    initialize_database(conn)
    return conn


def test_validate_execution_status_valid() -> None:
    assert validate_execution_status("Not Run") == "Not Run"
    assert validate_execution_status("passed") == "Passed"
    assert validate_execution_status("FAILED") == "Failed"
    assert validate_execution_status("blocked") == "Blocked"
    assert validate_execution_status("retest") == "Retest"


def test_validate_execution_status_invalid() -> None:
    with pytest.raises(TraceabilityValidationError, match="Invalid execution status"):
        validate_execution_status("UnknownStatus")

    with pytest.raises(TraceabilityValidationError, match="Invalid execution status"):
        validate_execution_status("InProgress")


def test_save_and_get_traceability_record(db_conn: sqlite3.Connection) -> None:
    test_cases = [
        {
            "test_case_id": "TC-001",
            "scenario": "Verify valid login",
            "test_type": "Functional",
            "priority": "High",
            "preconditions": ["User exists"],
            "test_steps": ["Submit credentials"],
            "expected_result": "Success",
        },
        {
            "test_case_id": "TC-002",
            "scenario": "Verify invalid login",
            "test_type": "Negative",
            "priority": "High",
            "preconditions": ["User exists"],
            "test_steps": ["Submit wrong password"],
            "expected_result": "Unauthorized error",
        },
    ]

    record = save_traceability_record(
        db_conn,
        requirement_id="REQ-AUTH-01",
        user_story="As a user, I want to log in securely.",
        test_cases=test_cases,
    )

    assert record["requirement_id"] == "REQ-AUTH-01"
    assert record["user_story"] == "As a user, I want to log in securely."
    assert len(record["test_cases"]) == 2
    assert record["test_cases"][0]["test_case_id"] == "TC-001"
    assert record["test_cases"][0]["execution_status"] == "Not Run"


def test_idempotent_save_traceability_record(db_conn: sqlite3.Connection) -> None:
    test_cases = [
        {
            "test_case_id": "TC-001",
            "scenario": "Verify item search",
            "test_type": "Functional",
            "priority": "Medium",
            "expected_result": "Search results returned",
        }
    ]

    # First save
    save_traceability_record(
        db_conn,
        requirement_id="REQ-SEARCH-01",
        user_story="User searches products",
        test_cases=test_cases,
    )

    # Second save with updated user story text
    updated_record = save_traceability_record(
        db_conn,
        requirement_id="REQ-SEARCH-01",
        user_story="User searches products with filter",
        test_cases=test_cases,
    )

    assert updated_record["user_story"] == "User searches products with filter"
    assert len(updated_record["test_cases"]) == 1

    # Verify no duplicate requirement records in DB
    all_records = list_traceability_records(db_conn)
    assert len(all_records) == 1


def test_test_case_collision_prevention(db_conn: sqlite3.Connection) -> None:
    # Link TC-100 to REQ-A
    save_traceability_record(
        db_conn,
        requirement_id="REQ-A",
        user_story="Story A",
        test_cases=[
            {"test_case_id": "TC-100", "scenario": "Scenario A", "expected_result": "Res A"}
        ],
    )

    # Attempting to assign TC-100 to REQ-B should fail
    with pytest.raises(TraceabilityValidationError, match="already linked to requirement 'REQ-A'"):
        save_traceability_record(
            db_conn,
            requirement_id="REQ-B",
            user_story="Story B",
            test_cases=[
                {"test_case_id": "TC-100", "scenario": "Scenario B", "expected_result": "Res B"}
            ],
        )



def test_update_traceability_test_case(db_conn: sqlite3.Connection) -> None:
    save_traceability_record(
        db_conn,
        requirement_id="REQ-ORDER-01",
        user_story="User places order",
        test_cases=[
            {
                "test_case_id": "TC-ORD-01",
                "scenario": "Place valid order",
                "expected_result": "Order created",
            }
        ],
    )

    updated_tc = update_traceability_test_case(
        db_conn,
        requirement_id="REQ-ORDER-01",
        test_case_id="TC-ORD-01",
        execution_status="Passed",
        actual_result="Order ID 1001 created successfully",
        defect_reference="DEFECT-NONE",
    )

    assert updated_tc["execution_status"] == "Passed"
    assert updated_tc["actual_result"] == "Order ID 1001 created successfully"
    assert updated_tc["defect_reference"] == "DEFECT-NONE"

    # Verify persisted in database query
    req = get_traceability_record(db_conn, "REQ-ORDER-01")
    assert req["test_cases"][0]["execution_status"] == "Passed"


def test_traceability_summary(db_conn: sqlite3.Connection) -> None:
    save_traceability_record(
        db_conn,
        requirement_id="REQ-SUM-01",
        user_story="Summary test requirement",
        test_cases=[
            {"test_case_id": "TC-01", "scenario": "S1", "expected_result": "E1"},
            {"test_case_id": "TC-02", "scenario": "S2", "expected_result": "E2"},
        ],
    )

    update_traceability_test_case(
        db_conn, requirement_id="REQ-SUM-01", test_case_id="TC-01", execution_status="Passed"
    )
    update_traceability_test_case(
        db_conn, requirement_id="REQ-SUM-01", test_case_id="TC-02", execution_status="Failed"
    )

    summary = get_traceability_summary(db_conn)
    assert summary["total_requirements"] == 1
    assert summary["total_test_cases"] == 2
    assert summary["passed"] == 1
    assert summary["failed"] == 1
    assert summary["not_run"] == 0


def test_get_nonexistent_requirement(db_conn: sqlite3.Connection) -> None:
    with pytest.raises(TraceabilityNotFoundError, match="Requirement 'REQ-MISSING' not found"):
        get_traceability_record(db_conn, "REQ-MISSING")


def test_foreign_key_enforcement(db_conn: sqlite3.Connection) -> None:
    # Attempt to insert directly into traceability_test_cases for a non-existent requirement_id
    with pytest.raises(sqlite3.IntegrityError):
        with db_conn:
            db_conn.execute(
                """
                INSERT INTO traceability_test_cases (
                  requirement_id, test_case_id, scenario, test_type, priority, expected_result
                ) VALUES (?, ?, ?, ?, ?, ?)
                """,
                ("NON-EXISTENT-REQ", "TC-FAIL", "Scen", "Functional", "High", "Exp"),
            )

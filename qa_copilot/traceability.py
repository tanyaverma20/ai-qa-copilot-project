from __future__ import annotations

import json
import sqlite3
from typing import Any

VALID_EXECUTION_STATUSES = {"Not Run", "Passed", "Failed", "Blocked", "Retest"}
VALID_TEST_TYPES = {"Functional", "Negative", "Boundary", "Regression"}
VALID_PRIORITIES = {"High", "Medium", "Low"}


class TraceabilityNotFoundError(Exception):
    """Raised when a requested requirement or test case does not exist."""


class TraceabilityValidationError(Exception):
    """Raised when validation fails for traceability records or parameters."""


def validate_execution_status(status: str) -> str:
    if not status or not isinstance(status, str):
        raise TraceabilityValidationError("Execution status must be a non-empty string.")

    # Normalize casing e.g. "passed" -> "Passed", "not run" -> "Not Run"
    cleaned = status.strip().title()
    if cleaned not in VALID_EXECUTION_STATUSES:
        raise TraceabilityValidationError(
            f"Invalid execution status '{status}'. Allowed values: "
            f"{', '.join(sorted(VALID_EXECUTION_STATUSES))}"
        )
    return cleaned


def _row_to_dict(row: sqlite3.Row) -> dict[str, Any]:
    return dict(row)


def _format_test_case_row(row: sqlite3.Row) -> dict[str, Any]:
    d = dict(row)
    pre_json = d.pop("preconditions_json", "[]")
    steps_json = d.pop("test_steps_json", "[]")

    try:
        d["preconditions"] = json.loads(pre_json) if isinstance(pre_json, str) else pre_json
    except json.JSONDecodeError:
        d["preconditions"] = []

    try:
        d["test_steps"] = json.loads(steps_json) if isinstance(steps_json, str) else steps_json
    except json.JSONDecodeError:
        d["test_steps"] = []

    return d


def save_traceability_record(
    connection: sqlite3.Connection,
    requirement_id: str,
    user_story: str,
    test_cases: list[dict[str, Any]],
) -> dict[str, Any]:
    req_id = (requirement_id or "").strip()
    if not req_id:
        raise TraceabilityValidationError("Requirement ID cannot be empty.")

    story = (user_story or "").strip()
    if not story:
        raise TraceabilityValidationError("User story text cannot be empty.")

    if not isinstance(test_cases, list) or len(test_cases) == 0:
        raise TraceabilityValidationError("Test cases list cannot be empty.")

    with connection:
        # Check for test case ID collisions under a different requirement ID
        for tc in test_cases:
            tc_id = str(tc.get("test_case_id") or tc.get("id") or "").strip()
            if not tc_id:
                raise TraceabilityValidationError(
                    "Each test case must have a non-empty test_case_id."
                )

            existing_conflict = connection.execute(
                """
                SELECT requirement_id FROM traceability_test_cases
                WHERE test_case_id = ? AND requirement_id != ?
                """,
                (tc_id, req_id),
            ).fetchone()

            if existing_conflict:
                other_req = existing_conflict["requirement_id"]
                raise TraceabilityValidationError(
                    f"Test case '{tc_id}' is already linked to requirement '{other_req}' "
                    f"and cannot be re-assigned to '{req_id}'."
                )

        # Idempotent requirement upsert
        connection.execute(
            """
            INSERT INTO traceability_requirements (requirement_id, user_story, updated_at)
            VALUES (?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(requirement_id) DO UPDATE SET
              user_story = excluded.user_story,
              updated_at = CURRENT_TIMESTAMP
            """,
            (req_id, story),
        )

        # Idempotent test cases upsert
        for tc in test_cases:
            tc_id = str(tc.get("test_case_id") or tc.get("id") or "").strip()
            scenario = str(tc.get("scenario") or "Unnamed Scenario").strip()
            test_type = str(tc.get("test_type") or "Functional").strip().title()
            if test_type not in VALID_TEST_TYPES:
                test_type = "Functional"

            priority = str(tc.get("priority") or "Medium").strip().title()
            if priority not in VALID_PRIORITIES:
                priority = "Medium"

            preconditions = tc.get("preconditions", [])
            if not isinstance(preconditions, list):
                preconditions = [str(preconditions)]
            preconditions_json = json.dumps([str(p) for p in preconditions])

            test_steps = tc.get("test_steps", [])
            if not isinstance(test_steps, list):
                test_steps = [str(test_steps)]
            test_steps_json = json.dumps([str(s) for s in test_steps])

            expected_result = str(tc.get("expected_result") or "").strip()
            execution_status = validate_execution_status(
                str(tc.get("execution_status") or "Not Run")
            )
            actual_result = str(tc.get("actual_result") or "").strip()
            defect_ref = str(tc.get("defect_reference") or tc.get("defect_ref") or "").strip()

            connection.execute(
                """
                INSERT INTO traceability_test_cases (
                  requirement_id, test_case_id, scenario, test_type, priority,
                  preconditions_json, test_steps_json, expected_result,
                  execution_status, actual_result, defect_reference, updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(requirement_id, test_case_id) DO UPDATE SET
                  scenario = excluded.scenario,
                  test_type = excluded.test_type,
                  priority = excluded.priority,
                  preconditions_json = excluded.preconditions_json,
                  test_steps_json = excluded.test_steps_json,
                  expected_result = excluded.expected_result,
                  updated_at = CURRENT_TIMESTAMP
                """,
                (
                    req_id,
                    tc_id,
                    scenario,
                    test_type,
                    priority,
                    preconditions_json,
                    test_steps_json,
                    expected_result,
                    execution_status,
                    actual_result,
                    defect_ref,
                ),
            )

    return get_traceability_record(connection, req_id)


def get_traceability_record(
    connection: sqlite3.Connection,
    requirement_id: str,
) -> dict[str, Any]:
    req_id = (requirement_id or "").strip()
    req_row = connection.execute(
        """
        SELECT requirement_id, user_story, created_at, updated_at
        FROM traceability_requirements WHERE requirement_id = ?
        """,
        (req_id,),
    ).fetchone()

    if not req_row:
        raise TraceabilityNotFoundError(f"Requirement '{req_id}' not found.")

    tc_rows = connection.execute(
        """
        SELECT id, requirement_id, test_case_id, scenario, test_type, priority,
               preconditions_json, test_steps_json, expected_result,
               execution_status, actual_result, defect_reference, created_at, updated_at
        FROM traceability_test_cases
        WHERE requirement_id = ?
        ORDER BY id
        """,
        (req_id,),
    ).fetchall()

    req_dict = _row_to_dict(req_row)
    req_dict["test_cases"] = [_format_test_case_row(row) for row in tc_rows]
    return req_dict


def list_traceability_records(connection: sqlite3.Connection) -> list[dict[str, Any]]:
    req_rows = connection.execute(
        """
        SELECT requirement_id, user_story, created_at, updated_at
        FROM traceability_requirements ORDER BY created_at DESC
        """
    ).fetchall()

    records = []
    for row in req_rows:
        records.append(get_traceability_record(connection, row["requirement_id"]))
    return records


def update_traceability_test_case(
    connection: sqlite3.Connection,
    requirement_id: str,
    test_case_id: str,
    execution_status: str | None = None,
    actual_result: str | None = None,
    defect_reference: str | None = None,
) -> dict[str, Any]:
    req_id = (requirement_id or "").strip()
    tc_id = (test_case_id or "").strip()

    tc_row = connection.execute(
        """
        SELECT id, requirement_id, test_case_id, scenario, test_type, priority,
               preconditions_json, test_steps_json, expected_result,
               execution_status, actual_result, defect_reference, created_at, updated_at
        FROM traceability_test_cases
        WHERE requirement_id = ? AND test_case_id = ?
        """,
        (req_id, tc_id),
    ).fetchone()

    if not tc_row:
        raise TraceabilityNotFoundError(
            f"Test case '{tc_id}' for requirement '{req_id}' not found."
        )

    current_dict = _format_test_case_row(tc_row)

    new_status = current_dict["execution_status"]
    if execution_status is not None:
        new_status = validate_execution_status(execution_status)

    new_actual = (
        actual_result.strip() if actual_result is not None else current_dict["actual_result"]
    )
    new_defect = (
        defect_reference.strip()
        if defect_reference is not None
        else current_dict["defect_reference"]
    )

    with connection:
        connection.execute(
            """
            UPDATE traceability_test_cases
            SET execution_status = ?,
                actual_result = ?,
                defect_reference = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE requirement_id = ? AND test_case_id = ?
            """,
            (new_status, new_actual, new_defect, req_id, tc_id),
        )

    updated_row = connection.execute(
        """
        SELECT id, requirement_id, test_case_id, scenario, test_type, priority,
               preconditions_json, test_steps_json, expected_result,
               execution_status, actual_result, defect_reference, created_at, updated_at
        FROM traceability_test_cases
        WHERE requirement_id = ? AND test_case_id = ?
        """,
        (req_id, tc_id),
    ).fetchone()

    return _format_test_case_row(updated_row)


def get_traceability_summary(connection: sqlite3.Connection) -> dict[str, int]:
    total_reqs = connection.execute(
        "SELECT COUNT(*) AS count FROM traceability_requirements"
    ).fetchone()["count"]
    total_tcs = connection.execute(
        "SELECT COUNT(*) AS count FROM traceability_test_cases"
    ).fetchone()["count"]

    status_counts = {"Passed": 0, "Failed": 0, "Blocked": 0, "Not Run": 0, "Retest": 0}
    rows = connection.execute(
        """
        SELECT execution_status, COUNT(*) AS count
        FROM traceability_test_cases GROUP BY execution_status
        """
    ).fetchall()


    for r in rows:
        st = r["execution_status"]
        if st in status_counts:
            status_counts[st] = r["count"]

    return {
        "total_requirements": total_reqs,
        "total_test_cases": total_tcs,
        "passed": status_counts["Passed"],
        "failed": status_counts["Failed"],
        "blocked": status_counts["Blocked"],
        "not_run": status_counts["Not Run"],
        "retest": status_counts["Retest"],
    }

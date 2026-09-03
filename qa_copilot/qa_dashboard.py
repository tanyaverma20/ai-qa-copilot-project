from __future__ import annotations

import sqlite3
from typing import Any

from qa_copilot.traceability import list_traceability_records


def get_qa_dashboard_data(
    connection: sqlite3.Connection,
    status: str | None = None,
    priority: str | None = None,
    test_type: str | None = None,
    requirement_id: str | None = None,
) -> dict[str, Any]:
    """Consolidates QA dashboard metrics and test case data from stored traceability records.

    Summary metrics are always calculated from the complete stored traceability dataset,
    ensuring global metrics remain consistent regardless of active list filters.
    """
    records = list_traceability_records(connection)

    all_test_cases: list[dict[str, Any]] = []
    total_requirements = len(records)

    for req in records:
        all_test_cases.extend(req.get("test_cases", []))

    total_test_cases = len(all_test_cases)
    passed = 0
    failed = 0
    blocked = 0
    retest = 0
    not_run = 0
    defect_count = 0
    regression_count = 0

    defect_cases: list[dict[str, Any]] = []
    regression_cases: list[dict[str, Any]] = []

    for tc in all_test_cases:
        st = tc.get("execution_status", "Not Run")
        if st == "Passed":
            passed += 1
        elif st == "Failed":
            failed += 1
        elif st == "Blocked":
            blocked += 1
        elif st == "Retest":
            retest += 1
        else:
            not_run += 1

        defect_ref = str(tc.get("defect_reference") or "").strip()
        if defect_ref:
            defect_count += 1

        is_defect_linked = st in ("Failed", "Blocked", "Retest") or bool(defect_ref)
        if is_defect_linked:
            defect_cases.append(tc)

        t_type = str(tc.get("test_type") or "").strip()
        if t_type.lower() == "regression":
            regression_count += 1
            regression_cases.append(tc)

    executed_test_cases = passed + failed + blocked + retest

    # Safely calculate pass rate excluding 'Not Run' from the denominator
    if executed_test_cases > 0:
        pass_rate = round((passed / executed_test_cases) * 100.0, 1)
    else:
        pass_rate = 0.0

    summary = {
        "total_requirements": total_requirements,
        "total_test_cases": total_test_cases,
        "executed_test_cases": executed_test_cases,
        "passed": passed,
        "failed": failed,
        "blocked": blocked,
        "retest": retest,
        "not_run": not_run,
        "pass_rate": pass_rate,
        "defect_count": defect_count,
        "regression_count": regression_count,
    }

    # Filter main test case list based on query parameters
    filtered_test_cases = []
    norm_status = status.strip().lower() if status and status.strip() else None
    norm_prio = priority.strip().lower() if priority and priority.strip() else None
    norm_type = test_type.strip().lower() if test_type and test_type.strip() else None
    norm_req = requirement_id.strip().lower() if requirement_id and requirement_id.strip() else None

    for tc in all_test_cases:
        tc_st = str(tc.get("execution_status") or "").strip().lower()
        tc_prio = str(tc.get("priority") or "").strip().lower()
        tc_type = str(tc.get("test_type") or "").strip().lower()
        tc_req = str(tc.get("requirement_id") or "").strip().lower()

        if norm_status and tc_st != norm_status:
            continue
        if norm_prio and tc_prio != norm_prio:
            continue
        if norm_type and tc_type != norm_type:
            continue
        if norm_req and norm_req not in tc_req:
            continue

        filtered_test_cases.append(tc)

    return {
        "summary": summary,
        "defect_cases": defect_cases,
        "regression_cases": regression_cases,
        "test_cases": filtered_test_cases,
    }

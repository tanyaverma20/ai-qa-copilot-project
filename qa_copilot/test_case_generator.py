from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass, field
from typing import Any

from qa_copilot.provider_health import provider_config_issues
from qa_copilot.providers import (
    DiagnosisProvider,
    DiagnosisProviderConfig,
    create_diagnosis_provider,
)


@dataclass
class TestCase:
    __test__ = False
    test_case_id: str
    requirement_id: str
    scenario: str
    preconditions: list[str] = field(default_factory=list)
    test_steps: list[str] = field(default_factory=list)
    expected_result: str = ""
    test_type: str = "Functional"
    priority: str = "Medium"


    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any], default_req_id: str = "REQ-001") -> TestCase:
        req_id = str(
            data.get("requirement_id") or data.get("requirement_story_id") or default_req_id
        ).strip()
        tc_id = str(data.get("test_case_id") or data.get("id") or "TC-001").strip()
        scenario = str(data.get("scenario") or data.get("title") or "Unnamed Scenario").strip()

        preconditions = data.get("preconditions", [])
        if isinstance(preconditions, str):
            preconditions = [p.strip() for p in preconditions.split("\n") if p.strip()]
        elif not isinstance(preconditions, list):
            preconditions = [str(preconditions)]
        else:
            preconditions = [str(p).strip() for p in preconditions if str(p).strip()]

        test_steps = data.get("test_steps", [])
        if isinstance(test_steps, str):
            test_steps = [s.strip() for s in test_steps.split("\n") if s.strip()]
        elif not isinstance(test_steps, list):
            test_steps = [str(test_steps)]
        else:
            test_steps = [str(s).strip() for s in test_steps if str(s).strip()]

        expected_result = str(data.get("expected_result") or data.get("expected") or "").strip()

        test_type = str(data.get("test_type") or "Functional").strip().title()
        if test_type not in ("Functional", "Negative", "Boundary", "Regression"):
            if "neg" in test_type.lower():
                test_type = "Negative"
            elif "bound" in test_type.lower():
                test_type = "Boundary"
            elif "regr" in test_type.lower():
                test_type = "Regression"
            else:
                test_type = "Functional"

        priority = str(data.get("priority") or "Medium").strip().title()
        if priority not in ("High", "Medium", "Low"):
            if "high" in priority.lower():
                priority = "High"
            elif "low" in priority.lower():
                priority = "Low"
            else:
                priority = "Medium"

        return cls(
            test_case_id=tc_id,
            requirement_id=req_id,
            scenario=scenario,
            preconditions=preconditions,
            test_steps=test_steps,
            expected_result=expected_result,
            test_type=test_type,
            priority=priority,
        )


@dataclass
class TestCaseGenerationResult:
    __test__ = False
    ok: bool
    requirement_id: str
    test_cases: list[TestCase] = field(default_factory=list)
    error: str | None = None
    raw_response: str | None = None


def build_test_case_prompt(user_story: str, requirement_id: str = "REQ-001") -> str:
    return f"""You are a Principal Software Quality Assurance Automation Architect.
Generate structured QA test cases for the following software requirement or user story.

Requirement ID: {requirement_id}
Requirement / User Story:
{user_story}

INSTRUCTIONS:
1. Cover Functional, Negative, Boundary, and Regression test types.
2. Return ONLY a raw JSON array containing test case objects.
   Do NOT include markdown codeblocks or conversational text.
3. Each object MUST strictly include the following keys:
   - "test_case_id": String (e.g., "TC-001", "TC-002")
   - "requirement_id": String (e.g., "{requirement_id}")
   - "scenario": String (describing the test objective)
   - "preconditions": Array of strings
   - "test_steps": Array of strings (ordered execution steps)
   - "expected_result": String (clear pass criteria)
   - "test_type": String ("Functional", "Negative", "Boundary", "Regression")
   - "priority": String ("High", "Medium", "Low")
"""



def parse_test_cases_response(raw_text: str, requirement_id: str = "REQ-001") -> list[TestCase]:
    if not raw_text or not raw_text.strip():
        return []

    text = raw_text.strip()
    # Remove markdown ```json ... ``` wrapper if present
    codeblock_match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text, re.IGNORECASE)
    if codeblock_match:
        text = codeblock_match.group(1).strip()

    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        # Fallback regex search for JSON array or object
        array_match = re.search(r"\[\s*\{[\s\S]*\}\s*\]", text)
        if array_match:
            try:
                data = json.loads(array_match.group(0))
            except json.JSONDecodeError:
                return []
        else:
            return []

    if isinstance(data, dict):
        if "test_cases" in data and isinstance(data["test_cases"], list):
            data = data["test_cases"]
        elif "testCases" in data and isinstance(data["testCases"], list):
            data = data["testCases"]
        else:
            data = [data]

    if not isinstance(data, list):
        return []

    test_cases: list[TestCase] = []
    for index, item in enumerate(data, start=1):
        if isinstance(item, dict):
            if not item.get("test_case_id"):
                item["test_case_id"] = f"TC-{index:03d}"
            item["requirement_id"] = item.get("requirement_id") or requirement_id
            test_cases.append(TestCase.from_dict(item, default_req_id=requirement_id))

    return test_cases


def generate_test_cases(
    user_story: str,
    requirement_id: str | None = None,
    provider: DiagnosisProvider | None = None,
    config: DiagnosisProviderConfig | None = None,
) -> TestCaseGenerationResult:
    req_id = (requirement_id or "REQ-001").strip()
    if not req_id:
        req_id = "REQ-001"

    if not user_story or not user_story.strip():
        raise ValueError("Requirement text cannot be empty or whitespace.")

    resolved_config = config or DiagnosisProviderConfig.from_env()
    missing_config, config_errors = provider_config_issues(resolved_config)
    if config_errors:
        return TestCaseGenerationResult(
            ok=False,
            requirement_id=req_id,
            error=f"AI provider configuration error: {', '.join(config_errors)}",
        )
    if "api_key" in missing_config:
        return TestCaseGenerationResult(
            ok=False,
            requirement_id=req_id,
            error="AI provider API key is not configured.",
        )
    if missing_config:
        return TestCaseGenerationResult(
            ok=False,
            requirement_id=req_id,
            error=f"AI provider configuration is missing: {', '.join(missing_config)}",
        )

    prompt = build_test_case_prompt(user_story=user_story.strip(), requirement_id=req_id)

    try:
        resolved_provider = provider or create_diagnosis_provider(resolved_config)
        raw_response = resolved_provider.generate(prompt)
        test_cases = parse_test_cases_response(raw_response, requirement_id=req_id)
        if not test_cases:
            return TestCaseGenerationResult(
                ok=False,
                requirement_id=req_id,
                error="Failed to parse structured test cases from LLM response.",
                raw_response=raw_response,
            )
        return TestCaseGenerationResult(
            ok=True,
            requirement_id=req_id,
            test_cases=test_cases,
            raw_response=raw_response,
        )
    except Exception as exc:
        return TestCaseGenerationResult(
            ok=False,
            requirement_id=req_id,
            error=f"AI provider generation failed: {str(exc)}",
        )

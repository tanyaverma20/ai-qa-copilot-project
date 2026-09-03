from __future__ import annotations

from pydantic import BaseModel, Field, field_validator


class LoginRequest(BaseModel):
    username: str = Field(min_length=1)
    password: str = Field(min_length=1)


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class OrderRequest(BaseModel):
    product_id: int = Field(gt=0)
    quantity: int = Field(gt=0)


class DiagnosisRequest(BaseModel):
    nodeid: str = Field(min_length=1)
    failed_at: str = Field(min_length=1)
    phase: str = Field(min_length=1)
    duration_seconds: float = Field(ge=0)
    longrepr: str = Field(min_length=1)
    keywords: list[str] = Field(default_factory=list)


class DiagnosisResponse(BaseModel):
    artifact_count: int
    report_markdown: str


class ProviderHealthResponse(BaseModel):
    ok: bool
    provider: str
    api_style: str
    api_key_configured: bool
    missing: list[str] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)


class TestCaseSchema(BaseModel):
    __test__ = False
    test_case_id: str
    requirement_id: str
    scenario: str
    preconditions: list[str] = Field(default_factory=list)
    test_steps: list[str] = Field(default_factory=list)
    expected_result: str
    test_type: str
    priority: str


class GenerateTestCasesRequest(BaseModel):
    user_story: str = Field(min_length=1)
    requirement_id: str | None = None


class GenerateTestCasesResponse(BaseModel):
    ok: bool
    requirement_id: str
    test_cases: list[TestCaseSchema] = Field(default_factory=list)
    error: str | None = None


VALID_EXECUTION_STATUSES = {"Not Run", "Passed", "Failed", "Blocked", "Retest"}


class TraceabilityTestCaseSchema(BaseModel):
    __test__ = False
    id: int | None = None
    requirement_id: str = Field(min_length=1)
    test_case_id: str = Field(min_length=1)
    scenario: str = Field(min_length=1)
    test_type: str = "Functional"
    priority: str = "Medium"
    preconditions: list[str] = Field(default_factory=list)
    test_steps: list[str] = Field(default_factory=list)
    expected_result: str = ""
    execution_status: str = "Not Run"
    actual_result: str = ""
    defect_reference: str = ""
    created_at: str | None = None
    updated_at: str | None = None

    @field_validator("execution_status")
    @classmethod
    def validate_status(cls, v: str) -> str:
        cleaned = v.strip().title()
        if cleaned not in VALID_EXECUTION_STATUSES:
            raise ValueError(
                f"Invalid execution_status '{v}'. Must be one of: "
                f"{', '.join(sorted(VALID_EXECUTION_STATUSES))}"
            )
        return cleaned


class TraceabilityRequirementSchema(BaseModel):
    __test__ = False
    requirement_id: str = Field(min_length=1)
    user_story: str = Field(min_length=1)
    created_at: str | None = None
    updated_at: str | None = None
    test_cases: list[TraceabilityTestCaseSchema] = Field(default_factory=list)


class CreateTraceabilityRecordRequest(BaseModel):
    requirement_id: str = Field(min_length=1)
    user_story: str = Field(min_length=1)
    test_cases: list[TestCaseSchema] = Field(min_length=1)


class UpdateTraceabilityTestCaseRequest(BaseModel):
    execution_status: str | None = None
    actual_result: str | None = None
    defect_reference: str | None = None

    @field_validator("execution_status")
    @classmethod
    def validate_status(cls, v: str | None) -> str | None:
        if v is None:
            return v
        cleaned = v.strip().title()
        if cleaned not in VALID_EXECUTION_STATUSES:
            raise ValueError(
                f"Invalid execution_status '{v}'. Must be one of: "
                f"{', '.join(sorted(VALID_EXECUTION_STATUSES))}"
            )
        return cleaned


class TraceabilitySummarySchema(BaseModel):
    total_requirements: int
    total_test_cases: int
    passed: int
    failed: int
    blocked: int
    not_run: int
    retest: int


class QADashboardSummarySchema(BaseModel):
    total_requirements: int
    total_test_cases: int
    executed_test_cases: int
    passed: int
    failed: int
    blocked: int
    retest: int
    not_run: int
    pass_rate: float
    defect_count: int
    regression_count: int


class QADashboardResponse(BaseModel):
    summary: QADashboardSummarySchema
    defect_cases: list[TraceabilityTestCaseSchema]
    regression_cases: list[TraceabilityTestCaseSchema]
    test_cases: list[TraceabilityTestCaseSchema]




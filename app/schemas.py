from __future__ import annotations

from pydantic import BaseModel, Field


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

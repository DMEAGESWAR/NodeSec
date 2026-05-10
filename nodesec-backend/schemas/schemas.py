import re
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, field_validator


# ── Auth ──

class UserRegisterRequest(BaseModel):
    email: str
    password: str
    org_name: str

    @field_validator("email")
    @classmethod
    def validate_email(cls, v):
        v = v.lower().strip()
        if "@" not in v:
            raise ValueError("Invalid email address")
        return v

    @field_validator("password")
    @classmethod
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        return v


class UserLoginRequest(BaseModel):
    email: str
    password: str


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict


# ── Domains ──

class DomainAddRequest(BaseModel):
    domain_name: str

    @field_validator("domain_name")
    @classmethod
    def validate_domain(cls, v):
        pattern = r'^([a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}$'
        if not re.match(pattern, v):
            raise ValueError("Invalid domain name format")
        return v.lower().strip()


class DomainResponse(BaseModel):
    id: UUID
    domain_name: str
    verified: bool
    demo_mode: bool
    created_at: datetime

    class Config:
        from_attributes = True


# ── Scan ──

class ScanStartRequest(BaseModel):
    domain_id: UUID
    is_demo: bool = False


class ScanStartResponse(BaseModel):
    scan_id: UUID
    status: str


class ScanResultResponse(BaseModel):
    id: UUID
    domain_id: UUID
    status: str
    overall_score: int | None
    started_at: datetime
    completed_at: datetime | None
    is_demo: bool
    nodes: list[dict]
    edges: list[dict]
    chains: list[dict]

    class Config:
        from_attributes = True


# ── SSE Events ──

class SSEEvent(BaseModel):
    event: str
    data: dict


# ── Findings ──

class FindingUpdateRequest(BaseModel):
    status: str | None = None
    assigned_to: str | None = None
    due_date: datetime | None = None


class FindingResponse(BaseModel):
    id: UUID
    scan_id: UUID
    chain_id: UUID
    status: str
    assigned_to: str | None
    due_date: datetime | None
    verified_at: datetime | None
    created_at: datetime

    class Config:
        from_attributes = True


# ── Report ──

class ReportRequest(BaseModel):
    scan_id: UUID

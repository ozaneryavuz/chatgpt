from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from .models import IncidentStatus, Priority, Role, TaskStatus


class ApiModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=10, max_length=200)
    organization_name: str = Field(min_length=2, max_length=180)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserOut(ApiModel):
    id: str
    email: EmailStr
    is_active: bool


class OrganizationOut(ApiModel):
    id: str
    name: str
    slug: str
    plan: str


class MembershipOut(ApiModel):
    organization: OrganizationOut
    role: Role


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut
    organization: OrganizationOut


class MemberCreate(BaseModel):
    email: EmailStr
    role: Role


class MemberOut(BaseModel):
    user_id: str
    email: EmailStr
    role: Role


class LocationCreate(BaseModel):
    name: str = Field(min_length=2, max_length=180)
    city: str | None = Field(default=None, max_length=100)
    district: str | None = Field(default=None, max_length=100)
    facility_type: str = Field(default="business", max_length=40)


class LocationOut(ApiModel):
    id: str
    organization_id: str
    name: str
    city: str | None
    district: str | None
    facility_type: str
    created_at: datetime


class CriticalLoadCreate(BaseModel):
    location_id: str
    name: str = Field(min_length=2, max_length=180)
    priority: Priority = Priority.p2
    power_kw: float | None = Field(default=None, ge=0)
    backup_source: str | None = Field(default=None, max_length=120)
    autonomy_minutes: int | None = Field(default=None, ge=0)
    owner_name: str | None = Field(default=None, max_length=120)


class CriticalLoadOut(ApiModel):
    id: str
    organization_id: str
    location_id: str
    name: str
    priority: Priority
    power_kw: float | None
    backup_source: str | None
    autonomy_minutes: int | None
    owner_name: str | None


class AssetCreate(BaseModel):
    location_id: str
    kind: str = Field(max_length=40)
    name: str = Field(min_length=2, max_length=180)
    rated_power_kva: float | None = Field(default=None, ge=0)
    test_interval_days: int | None = Field(default=None, ge=1)


class AssetOut(ApiModel):
    id: str
    organization_id: str
    location_id: str
    kind: str
    name: str
    rated_power_kva: float | None
    test_interval_days: int | None
    last_test_at: datetime | None


class AssetTestCreate(BaseModel):
    result: str = Field(pattern="^(passed|failed|conditional)$")
    notes: str | None = Field(default=None, max_length=2000)
    tested_at: datetime | None = None


class AssetTestOut(ApiModel):
    id: str
    organization_id: str
    asset_id: str
    result: str
    notes: str | None
    tested_at: datetime
    created_by_user_id: str


class IncidentCreate(BaseModel):
    location_id: str
    kind: str = Field(default="outage", max_length=40)
    summary: str | None = Field(default=None, max_length=2000)


class TaskOut(ApiModel):
    id: str
    incident_id: str
    title: str
    priority: Priority
    is_required: bool
    status: TaskStatus
    assignee_name: str | None
    completed_at: datetime | None


class IncidentOut(ApiModel):
    id: str
    organization_id: str
    location_id: str
    kind: str
    status: IncidentStatus
    summary: str | None
    started_at: datetime
    ended_at: datetime | None
    created_by_user_id: str
    tasks: list[TaskOut] = []


class CloseIncidentRequest(BaseModel):
    closure_note: str | None = Field(default=None, max_length=2000)


class AuditOut(ApiModel):
    id: str
    user_id: str
    action: str
    entity_type: str
    entity_id: str
    details_json: str | None
    created_at: datetime

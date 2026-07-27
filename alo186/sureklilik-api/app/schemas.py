from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_serializer

from .models import IncidentStatus, Priority, Role, TaskStatus


class ApiModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    @field_serializer("*", when_used="json", check_fields=False)
    def serialize_utc_datetimes(self, value):
        """SQLite dahil bütün backend'lerde UTC tarihleri aynı `Z` biçiminde döndürür."""
        if isinstance(value, datetime):
            aware = value if value.tzinfo is not None else value.replace(tzinfo=timezone.utc)
            return aware.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
        return value


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=10, max_length=200)
    organization_name: str = Field(min_length=2, max_length=180)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str
    mfa_code: str | None = Field(default=None, min_length=6, max_length=32)


class GenericMessage(BaseModel):
    message: str
    test_token: str | None = None


class TokenConfirmRequest(BaseModel):
    token: str = Field(min_length=20, max_length=300)


class PasswordResetRequest(BaseModel):
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    token: str = Field(min_length=20, max_length=300)
    new_password: str = Field(min_length=10, max_length=200)


class UserOut(ApiModel):
    id: str
    email: EmailStr
    is_active: bool
    is_email_verified: bool
    mfa_enabled: bool
    deletion_requested_at: datetime | None = None


class OrganizationOut(ApiModel):
    id: str
    name: str
    slug: str
    plan: str
    subscription_status: str
    plan_expires_at: datetime | None
    is_active: bool


class MembershipOut(ApiModel):
    organization: OrganizationOut
    role: Role
    notify_incidents: bool


class AuthResponse(ApiModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut
    organization: OrganizationOut
    email_verification_required: bool = False


class SessionOut(ApiModel):
    id: str
    created_at: datetime
    last_seen_at: datetime
    expires_at: datetime
    revoked_at: datetime | None


class MfaSetupOut(BaseModel):
    secret: str
    provisioning_uri: str


class MfaCodeRequest(BaseModel):
    code: str = Field(min_length=6, max_length=32)


class MfaEnableOut(BaseModel):
    enabled: bool = True
    recovery_codes: list[str]


class MfaDisableRequest(BaseModel):
    password: str
    code: str = Field(min_length=6, max_length=32)


class MfaRecoveryRegenerateRequest(MfaDisableRequest):
    pass


class AccountDeletionRequest(BaseModel):
    password: str
    confirmation: str = Field(pattern="^HESABIMI SIL$")


class OrganizationDeletionRequest(BaseModel):
    password: str
    organization_name: str


class MemberCreate(BaseModel):
    email: EmailStr
    role: Role
    notify_incidents: bool = True


class MemberOut(BaseModel):
    user_id: str
    email: EmailStr
    role: Role
    notify_incidents: bool


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
    created_by_user_id: str | None


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
    created_by_user_id: str | None
    tasks: list[TaskOut] = []


class CloseIncidentRequest(BaseModel):
    closure_note: str | None = Field(default=None, max_length=2000)


class AuditOut(ApiModel):
    id: str
    user_id: str | None
    action: str
    entity_type: str
    entity_id: str
    details_json: str | None
    created_at: datetime


class BillingUsageOut(ApiModel):
    plan: str
    subscription_status: str
    plan_expires_at: datetime | None
    usage: dict[str, int]
    limits: dict[str, int | None]
    remaining: dict[str, int | None]


class PrivacyExportOut(BaseModel):
    data: dict[str, Any]

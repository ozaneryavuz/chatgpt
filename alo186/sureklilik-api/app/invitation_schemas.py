from __future__ import annotations

from datetime import datetime, timezone

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_serializer

from .models import Role
from .schemas import AuthResponse


class InvitationCreate(BaseModel):
    email: EmailStr
    role: Role = Role.viewer
    notify_incidents: bool = True


class InvitationAcceptRequest(BaseModel):
    token: str = Field(min_length=20, max_length=300)
    password: str | None = Field(default=None, min_length=10, max_length=200)


class InvitationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    organization_id: str
    email: EmailStr
    role: Role
    notify_incidents: bool
    expires_at: datetime
    accepted_at: datetime | None
    revoked_at: datetime | None
    status: str
    created_at: datetime
    test_token: str | None = None

    @field_serializer("expires_at", "accepted_at", "revoked_at", "created_at", when_used="json")
    def serialize_datetime(self, value):
        if value is None:
            return None
        aware = value if value.tzinfo is not None else value.replace(tzinfo=timezone.utc)
        return aware.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


class InvitationPreview(BaseModel):
    organization_name: str
    email: EmailStr
    role: Role
    notify_incidents: bool
    expires_at: datetime
    existing_user: bool

    @field_serializer("expires_at", when_used="json")
    def serialize_datetime(self, value):
        aware = value if value.tzinfo is not None else value.replace(tzinfo=timezone.utc)
        return aware.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


class InvitationAcceptResponse(AuthResponse):
    created_user: bool
    invitation_id: str

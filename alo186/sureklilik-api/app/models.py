from __future__ import annotations

import enum
import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Enum, Float, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .db import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def new_id() -> str:
    return str(uuid.uuid4())


class Role(str, enum.Enum):
    admin = "admin"
    technician = "technician"
    viewer = "viewer"


class Priority(str, enum.Enum):
    p1 = "P1"
    p2 = "P2"
    p3 = "P3"


class IncidentStatus(str, enum.Enum):
    open = "open"
    closed = "closed"


class TaskStatus(str, enum.Enum):
    open = "open"
    completed = "completed"


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    email: Mapped[str] = mapped_column(String(320), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_email_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    email_verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    token_version: Mapped[int] = mapped_column(Integer, default=1)
    failed_login_count: Mapped[int] = mapped_column(Integer, default=0)
    locked_until: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    password_changed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    mfa_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    mfa_secret_ciphertext: Mapped[str | None] = mapped_column(Text, nullable=True)
    mfa_recovery_codes_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    deletion_requested_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    deletion_execute_after: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    memberships: Mapped[list["Membership"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    sessions: Mapped[list["AuthSession"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    auth_tokens: Mapped[list["AuthToken"]] = relationship(back_populates="user", cascade="all, delete-orphan")


class Organization(Base):
    __tablename__ = "organizations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    name: Mapped[str] = mapped_column(String(180))
    slug: Mapped[str] = mapped_column(String(180), unique=True, index=True)
    plan: Mapped[str] = mapped_column(String(40), default="pilot")
    subscription_status: Mapped[str] = mapped_column(String(40), default="trial")
    plan_expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    deletion_requested_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    deletion_execute_after: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    memberships: Mapped[list["Membership"]] = relationship(back_populates="organization", cascade="all, delete-orphan")


class Membership(Base):
    __tablename__ = "memberships"
    __table_args__ = (UniqueConstraint("user_id", "organization_id", name="uq_membership_user_org"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    organization_id: Mapped[str] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"), index=True)
    role: Mapped[Role] = mapped_column(Enum(Role), default=Role.viewer)
    notify_incidents: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    user: Mapped[User] = relationship(back_populates="memberships")
    organization: Mapped[Organization] = relationship(back_populates="memberships")


class AuthSession(Base):
    __tablename__ = "auth_sessions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    token_version: Mapped[int] = mapped_column(Integer)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    ip_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)
    user_agent_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    last_seen_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    user: Mapped[User] = relationship(back_populates="sessions")


class AuthToken(Base):
    __tablename__ = "auth_tokens"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    purpose: Mapped[str] = mapped_column(String(40), index=True)
    token_hash: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    consumed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    request_ip_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    user: Mapped[User] = relationship(back_populates="auth_tokens")


class EmailOutbox(Base):
    __tablename__ = "email_outbox"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    user_id: Mapped[str | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    organization_id: Mapped[str | None] = mapped_column(ForeignKey("organizations.id", ondelete="SET NULL"), nullable=True, index=True)
    to_email: Mapped[str] = mapped_column(String(320), index=True)
    template: Mapped[str] = mapped_column(String(80))
    subject: Mapped[str] = mapped_column(String(240))
    payload_json: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(30), default="pending", index=True)
    attempts: Mapped[int] = mapped_column(Integer, default=0)
    available_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, index=True)
    sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_error: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class Location(Base):
    __tablename__ = "locations"
    __table_args__ = (UniqueConstraint("organization_id", "name", name="uq_location_org_name"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    organization_id: Mapped[str] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(180))
    city: Mapped[str | None] = mapped_column(String(100), nullable=True)
    district: Mapped[str | None] = mapped_column(String(100), nullable=True)
    facility_type: Mapped[str] = mapped_column(String(40), default="business")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class CriticalLoad(Base):
    __tablename__ = "critical_loads"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    organization_id: Mapped[str] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"), index=True)
    location_id: Mapped[str] = mapped_column(ForeignKey("locations.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(180))
    priority: Mapped[Priority] = mapped_column(Enum(Priority), default=Priority.p2)
    power_kw: Mapped[float | None] = mapped_column(Float, nullable=True)
    backup_source: Mapped[str | None] = mapped_column(String(120), nullable=True)
    autonomy_minutes: Mapped[int | None] = mapped_column(nullable=True)
    owner_name: Mapped[str | None] = mapped_column(String(120), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class Asset(Base):
    __tablename__ = "assets"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    organization_id: Mapped[str] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"), index=True)
    location_id: Mapped[str] = mapped_column(ForeignKey("locations.id", ondelete="CASCADE"), index=True)
    kind: Mapped[str] = mapped_column(String(40))
    name: Mapped[str] = mapped_column(String(180))
    rated_power_kva: Mapped[float | None] = mapped_column(Float, nullable=True)
    test_interval_days: Mapped[int | None] = mapped_column(nullable=True)
    last_test_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class AssetTest(Base):
    __tablename__ = "asset_tests"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    organization_id: Mapped[str] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"), index=True)
    asset_id: Mapped[str] = mapped_column(ForeignKey("assets.id", ondelete="CASCADE"), index=True)
    result: Mapped[str] = mapped_column(String(30))
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    tested_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    created_by_user_id: Mapped[str] = mapped_column(ForeignKey("users.id"))


class Incident(Base):
    __tablename__ = "incidents"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    organization_id: Mapped[str] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"), index=True)
    location_id: Mapped[str] = mapped_column(ForeignKey("locations.id", ondelete="CASCADE"), index=True)
    kind: Mapped[str] = mapped_column(String(40), default="outage")
    status: Mapped[IncidentStatus] = mapped_column(Enum(IncidentStatus), default=IncidentStatus.open)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    ended_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_by_user_id: Mapped[str] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    tasks: Mapped[list["IncidentTask"]] = relationship(back_populates="incident", cascade="all, delete-orphan")


class IncidentTask(Base):
    __tablename__ = "incident_tasks"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    organization_id: Mapped[str] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"), index=True)
    incident_id: Mapped[str] = mapped_column(ForeignKey("incidents.id", ondelete="CASCADE"), index=True)
    title: Mapped[str] = mapped_column(String(260))
    priority: Mapped[Priority] = mapped_column(Enum(Priority), default=Priority.p2)
    is_required: Mapped[bool] = mapped_column(Boolean, default=False)
    status: Mapped[TaskStatus] = mapped_column(Enum(TaskStatus), default=TaskStatus.open)
    assignee_name: Mapped[str | None] = mapped_column(String(120), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    incident: Mapped[Incident] = relationship(back_populates="tasks")


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    organization_id: Mapped[str] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"), index=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"))
    action: Mapped[str] = mapped_column(String(80))
    entity_type: Mapped[str] = mapped_column(String(80))
    entity_id: Mapped[str] = mapped_column(String(36))
    details_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

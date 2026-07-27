from __future__ import annotations

import json
import logging
import time
from contextlib import asynccontextmanager
from datetime import timedelta

from fastapi import Depends, FastAPI, HTTPException, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse, PlainTextResponse
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload

from .audit import write_audit
from .auth_service import (
    account_is_locked,
    consume_one_time_token,
    create_session,
    issue_one_time_token,
    recovery_code_count,
    register_failed_login,
    register_successful_login,
    revoke_all_sessions,
    revoke_session,
    verify_user_mfa,
)
from .config import settings
from .db import check_db, init_db
from .deps import OrgContext, get_current_user, get_db, get_org_context, require_roles
from .models import (
    Asset,
    AssetTest,
    AuditLog,
    AuthSession,
    CriticalLoad,
    Incident,
    IncidentStatus,
    IncidentTask,
    Location,
    Membership,
    Organization,
    Role,
    TaskStatus,
    User,
)
from .notifications import incident_email, password_reset_email, verification_email
from .observability import configure_logging, metrics, request_id
from .plans import enforce_limit, usage_snapshot
from .privacy import organization_export, request_organization_deletion, request_user_deletion, user_export
from .rate_limit import check_global_rate, client_ip, enforce_auth_rate
from .schemas import (
    AccountDeletionRequest,
    AssetCreate,
    AssetOut,
    AssetTestCreate,
    AssetTestOut,
    AuditOut,
    AuthResponse,
    BillingUsageOut,
    CloseIncidentRequest,
    CriticalLoadCreate,
    CriticalLoadOut,
    GenericMessage,
    IncidentCreate,
    IncidentOut,
    LocationCreate,
    LocationOut,
    LoginRequest,
    MemberCreate,
    MemberOut,
    MembershipOut,
    MfaCodeRequest,
    MfaDisableRequest,
    MfaEnableOut,
    MfaRecoveryRegenerateRequest,
    MfaSetupOut,
    OrganizationDeletionRequest,
    OrganizationOut,
    PasswordResetConfirm,
    PasswordResetRequest,
    PrivacyExportOut,
    RegisterRequest,
    SessionOut,
    TaskOut,
    TokenConfirmRequest,
    UserOut,
)
from .security import (
    decrypt_secret,
    encrypt_secret,
    generate_recovery_codes,
    generate_totp_secret,
    hash_client_value,
    hash_password,
    hash_recovery_code,
    totp_provisioning_uri,
    verify_password,
    verify_totp,
)
from .service import build_incident_tasks, unique_slug, utcnow

configure_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="ALO186 Elektrik Sürekliliği API",
    version="0.3.0",
    description=(
        "Otel, site ve işletmeler için e-posta doğrulamalı, MFA destekli, "
        "tenant izolasyonlu elektrik sürekliliği SaaS API temeli."
    ),
    lifespan=lifespan,
)

app.add_middleware(TrustedHostMiddleware, allowed_hosts=list(settings.allowed_hosts))
app.add_middleware(
    CORSMiddleware,
    allow_origins=list(settings.allowed_origins),
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
    allow_headers=[
        "Authorization",
        "Content-Type",
        "X-Organization-ID",
        "X-Request-ID",
        "X-Metrics-Token",
    ],
    expose_headers=["X-Request-ID", "X-RateLimit-Limit", "X-RateLimit-Remaining"],
)


@app.middleware("http")
async def request_security_and_metrics(request: Request, call_next):
    req_id = request_id(request.headers.get("x-request-id"))
    request.state.request_id = req_id
    content_length = request.headers.get("content-length")
    if content_length:
        try:
            if int(content_length) > settings.max_request_bytes:
                return JSONResponse(
                    status_code=413,
                    content={"detail": "İstek gövdesi izin verilen sınırı aşıyor."},
                    headers={"X-Request-ID": req_id},
                )
        except ValueError:
            return JSONResponse(
                status_code=400,
                content={"detail": "Geçersiz Content-Length başlığı."},
                headers={"X-Request-ID": req_id},
            )

    rate_result = None
    if request.url.path not in {"/health", "/health/live", "/health/ready", "/metrics"}:
        rate_result = check_global_rate(request)
        if not rate_result.allowed:
            return JSONResponse(
                status_code=429,
                content={"detail": "Çok fazla istek. Kısa süre sonra tekrar deneyin."},
                headers={
                    "Retry-After": str(rate_result.retry_after),
                    "X-Request-ID": req_id,
                },
            )

    metrics.enter()
    started = time.perf_counter()
    response: Response | None = None
    try:
        response = await call_next(request)
        return response
    except Exception:
        logger.exception(
            "request_failed",
            extra={
                "request_id": req_id,
                "method": request.method,
                "path": request.url.path,
                "client_ip_hash": hash_client_value(client_ip(request)),
            },
        )
        raise
    finally:
        duration = time.perf_counter() - started
        route = request.scope.get("route")
        path_template = getattr(route, "path", request.url.path)
        status_code = response.status_code if response is not None else 500
        metrics.observe(
            method=request.method,
            path=path_template,
            status_code=status_code,
            duration_seconds=duration,
        )
        if response is not None:
            response.headers["X-Request-ID"] = req_id
            response.headers["X-Content-Type-Options"] = "nosniff"
            response.headers["X-Frame-Options"] = "DENY"
            response.headers["Referrer-Policy"] = "no-referrer"
            response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
            if request.url.path.startswith("/api/v1/auth") or request.url.path.startswith("/api/v1/privacy"):
                response.headers["Cache-Control"] = "no-store"
            if rate_result is not None:
                response.headers["X-RateLimit-Limit"] = str(settings.global_rate_limit)
                response.headers["X-RateLimit-Remaining"] = str(rate_result.remaining)
            logger.info(
                "request_completed",
                extra={
                    "request_id": req_id,
                    "method": request.method,
                    "path": path_template,
                    "status_code": status_code,
                    "duration_ms": round(duration * 1_000, 2),
                    "client_ip_hash": hash_client_value(client_ip(request)),
                    "user_id": getattr(request.state, "user_id", None),
                },
            )


def incident_query(organization_id: str):
    return (
        select(Incident)
        .options(selectinload(Incident.tasks))
        .where(Incident.organization_id == organization_id)
    )


def queue_incident_notifications(
    db: Session,
    *,
    organization: Organization,
    incident: Incident,
    action: str,
) -> int:
    rows = db.execute(
        select(Membership, User)
        .join(User, User.id == Membership.user_id)
        .where(
            Membership.organization_id == organization.id,
            Membership.notify_incidents.is_(True),
            User.is_email_verified.is_(True),
            User.is_active.is_(True),
        )
    ).all()
    for _membership, user in rows:
        incident_email(
            db,
            user_id=user.id,
            organization_id=organization.id,
            email=user.email,
            organization_name=organization.name,
            incident_id=incident.id,
            action=action,
            summary=incident.summary or "Elektrik sürekliliği olayı güncellendi.",
        )
    return len(rows)


@app.get("/health")
@app.get("/health/live")
def health() -> dict[str, str]:
    return {"status": "ok", "version": app.version}


@app.get("/health/ready")
def readiness() -> dict[str, str]:
    try:
        check_db()
    except Exception as exc:
        raise HTTPException(status_code=503, detail="Veri tabanı hazır değil.") from exc
    return {"status": "ready", "database": "ok", "version": app.version}


@app.get("/metrics", response_class=PlainTextResponse)
def prometheus_metrics(request: Request) -> str:
    if settings.metrics_token:
        supplied = request.headers.get("x-metrics-token")
        if supplied != settings.metrics_token:
            raise HTTPException(status_code=403, detail="Metrics erişimi reddedildi.")
    return metrics.render_prometheus()


@app.post("/api/v1/auth/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest, request: Request, db: Session = Depends(get_db)) -> AuthResponse:
    email = payload.email.lower()
    enforce_auth_rate(request, email)
    if db.scalar(select(User.id).where(User.email == email)):
        raise HTTPException(status_code=409, detail="Bu e-posta zaten kayıtlı.")
    user = User(
        email=email,
        password_hash=hash_password(payload.password),
        is_email_verified=not settings.email_verification_required,
        email_verified_at=utcnow() if not settings.email_verification_required else None,
    )
    organization = Organization(
        name=payload.organization_name,
        slug=unique_slug(db, payload.organization_name, Organization),
    )
    membership = Membership(user=user, organization=organization, role=Role.admin)
    db.add_all([user, organization, membership])
    try:
        db.flush()
        test_token = None
        if settings.email_verification_required:
            test_token = issue_one_time_token(
                db,
                user=user,
                purpose="email_verification",
                ttl_seconds=settings.email_token_ttl_seconds,
                request=request,
            )
            verification_email(db, user_id=user.id, email=user.email, token=test_token)
        access_token, _session = create_session(db, user, request)
        write_audit(
            db,
            organization_id=organization.id,
            user_id=user.id,
            action="organization.created",
            entity_type="organization",
            entity_id=organization.id,
            details={"email_verification_required": settings.email_verification_required},
        )
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="Kayıt oluşturulamadı.") from exc
    return AuthResponse(
        access_token=access_token,
        user=UserOut.model_validate(user),
        organization=OrganizationOut.model_validate(organization),
        email_verification_required=settings.email_verification_required and not user.is_email_verified,
    )


@app.post("/api/v1/auth/login", response_model=AuthResponse)
def login(payload: LoginRequest, request: Request, db: Session = Depends(get_db)) -> AuthResponse:
    email = payload.email.lower()
    enforce_auth_rate(request, email)
    user = db.scalar(select(User).where(User.email == email))
    if user and account_is_locked(user):
        db.commit()
        raise HTTPException(status_code=423, detail="Hesap geçici olarak kilitli. Daha sonra tekrar deneyin.")
    if not user or not verify_password(payload.password, user.password_hash):
        register_failed_login(db, user)
        db.commit()
        raise HTTPException(status_code=401, detail="E-posta veya parola hatalı.")
    if not user.is_active or user.deleted_at is not None:
        raise HTTPException(status_code=401, detail="E-posta veya parola hatalı.")
    verify_user_mfa(user, payload.mfa_code)
    membership = db.scalar(
        select(Membership)
        .options(selectinload(Membership.organization))
        .where(Membership.user_id == user.id)
        .order_by(Membership.created_at)
    )
    if not membership or not membership.organization.is_active:
        raise HTTPException(status_code=403, detail="Etkin kuruluş üyeliği bulunamadı.")
    register_successful_login(db, user)
    access_token, _session = create_session(db, user, request)
    write_audit(
        db,
        organization_id=membership.organization_id,
        user_id=user.id,
        action="auth.login",
        entity_type="user",
        entity_id=user.id,
        details={"mfa": user.mfa_enabled},
    )
    db.commit()
    return AuthResponse(
        access_token=access_token,
        user=UserOut.model_validate(user),
        organization=OrganizationOut.model_validate(membership.organization),
        email_verification_required=settings.email_verification_required and not user.is_email_verified,
    )


@app.post("/api/v1/auth/logout", response_model=GenericMessage)
def logout(request: Request, user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> GenericMessage:
    revoke_session(db, request.state.auth_session_id)
    db.commit()
    return GenericMessage(message="Oturum kapatıldı.")


@app.post("/api/v1/auth/logout-all", response_model=GenericMessage)
def logout_all(user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> GenericMessage:
    count = revoke_all_sessions(db, user)
    db.commit()
    return GenericMessage(message=f"{count} oturum iptal edildi.")


@app.get("/api/v1/auth/sessions", response_model=list[SessionOut])
def list_sessions(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.scalars(
        select(AuthSession)
        .where(AuthSession.user_id == user.id)
        .order_by(AuthSession.created_at.desc())
        .limit(100)
    ).all()


@app.delete("/api/v1/auth/sessions/{session_id}", response_model=GenericMessage)
def delete_session(
    session_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> GenericMessage:
    session = db.scalar(select(AuthSession).where(AuthSession.id == session_id, AuthSession.user_id == user.id))
    if not session:
        raise HTTPException(status_code=404, detail="Oturum bulunamadı.")
    revoke_session(db, session.id)
    db.commit()
    return GenericMessage(message="Oturum iptal edildi.")


@app.post("/api/v1/auth/email-verification/request", response_model=GenericMessage, status_code=202)
def request_email_verification(
    payload: PasswordResetRequest,
    request: Request,
    db: Session = Depends(get_db),
) -> GenericMessage:
    enforce_auth_rate(request, payload.email.lower())
    user = db.scalar(select(User).where(User.email == payload.email.lower()))
    test_token = None
    if user and user.is_active and not user.is_email_verified:
        test_token = issue_one_time_token(
            db,
            user=user,
            purpose="email_verification",
            ttl_seconds=settings.email_token_ttl_seconds,
            request=request,
        )
        verification_email(db, user_id=user.id, email=user.email, token=test_token)
        db.commit()
    return GenericMessage(
        message="Hesap uygunsa doğrulama iletisi gönderildi.",
        test_token=test_token if settings.expose_test_tokens else None,
    )


@app.post("/api/v1/auth/email-verification/confirm", response_model=GenericMessage)
def confirm_email_verification(payload: TokenConfirmRequest, db: Session = Depends(get_db)) -> GenericMessage:
    user = consume_one_time_token(db, raw_token=payload.token, purpose="email_verification")
    user.is_email_verified = True
    user.email_verified_at = utcnow()
    db.commit()
    return GenericMessage(message="E-posta adresi doğrulandı.")


@app.post("/api/v1/auth/password-reset/request", response_model=GenericMessage, status_code=202)
def request_password_reset(
    payload: PasswordResetRequest,
    request: Request,
    db: Session = Depends(get_db),
) -> GenericMessage:
    enforce_auth_rate(request, payload.email.lower())
    user = db.scalar(select(User).where(User.email == payload.email.lower()))
    test_token = None
    if user and user.is_active:
        test_token = issue_one_time_token(
            db,
            user=user,
            purpose="password_reset",
            ttl_seconds=settings.password_reset_ttl_seconds,
            request=request,
        )
        password_reset_email(db, user_id=user.id, email=user.email, token=test_token)
        db.commit()
    return GenericMessage(
        message="Hesap uygunsa parola sıfırlama iletisi gönderildi.",
        test_token=test_token if settings.expose_test_tokens else None,
    )


@app.post("/api/v1/auth/password-reset/confirm", response_model=GenericMessage)
def confirm_password_reset(payload: PasswordResetConfirm, db: Session = Depends(get_db)) -> GenericMessage:
    user = consume_one_time_token(db, raw_token=payload.token, purpose="password_reset")
    user.password_hash = hash_password(payload.new_password)
    user.password_changed_at = utcnow()
    user.is_email_verified = True
    user.email_verified_at = user.email_verified_at or utcnow()
    revoke_all_sessions(db, user)
    db.commit()
    return GenericMessage(message="Parola yenilendi; mevcut oturumlar iptal edildi.")


@app.post("/api/v1/auth/mfa/setup", response_model=MfaSetupOut)
def mfa_setup(user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> MfaSetupOut:
    if settings.email_verification_required and not user.is_email_verified:
        raise HTTPException(status_code=403, detail="MFA öncesinde e-posta doğrulaması gerekli.")
    if user.mfa_enabled:
        raise HTTPException(status_code=409, detail="MFA zaten etkin.")
    secret = generate_totp_secret()
    user.mfa_secret_ciphertext = encrypt_secret(secret)
    user.mfa_recovery_codes_json = None
    db.commit()
    return MfaSetupOut(secret=secret, provisioning_uri=totp_provisioning_uri(secret, user.email))


@app.post("/api/v1/auth/mfa/enable", response_model=MfaEnableOut)
def mfa_enable(
    payload: MfaCodeRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> MfaEnableOut:
    if user.mfa_enabled:
        raise HTTPException(status_code=409, detail="MFA zaten etkin.")
    if not user.mfa_secret_ciphertext:
        raise HTTPException(status_code=409, detail="Önce MFA kurulumunu başlatın.")
    secret = decrypt_secret(user.mfa_secret_ciphertext)
    if not verify_totp(payload.code, secret):
        raise HTTPException(status_code=400, detail="MFA kodu geçersiz.")
    recovery_codes = generate_recovery_codes()
    user.mfa_recovery_codes_json = json.dumps([hash_recovery_code(code) for code in recovery_codes])
    user.mfa_enabled = True
    db.commit()
    return MfaEnableOut(recovery_codes=recovery_codes)


@app.post("/api/v1/auth/mfa/recovery-codes", response_model=MfaEnableOut)
def regenerate_mfa_recovery_codes(
    payload: MfaRecoveryRegenerateRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> MfaEnableOut:
    if not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Parola hatalı.")
    verify_user_mfa(user, payload.code)
    recovery_codes = generate_recovery_codes()
    user.mfa_recovery_codes_json = json.dumps([hash_recovery_code(code) for code in recovery_codes])
    db.commit()
    return MfaEnableOut(recovery_codes=recovery_codes)


@app.post("/api/v1/auth/mfa/disable", response_model=GenericMessage)
def mfa_disable(
    payload: MfaDisableRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> GenericMessage:
    if not user.mfa_enabled:
        return GenericMessage(message="MFA zaten kapalı.")
    if not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Parola hatalı.")
    verify_user_mfa(user, payload.code)
    user.mfa_enabled = False
    user.mfa_secret_ciphertext = None
    user.mfa_recovery_codes_json = None
    revoke_all_sessions(db, user)
    db.commit()
    return GenericMessage(message="MFA kapatıldı; bütün oturumlar iptal edildi.")


@app.get("/api/v1/auth/me", response_model=UserOut)
def me(user: User = Depends(get_current_user)) -> User:
    return user


@app.get("/api/v1/auth/memberships", response_model=list[MembershipOut])
def memberships(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.scalars(
        select(Membership)
        .options(selectinload(Membership.organization))
        .where(Membership.user_id == user.id)
    ).all()


@app.get("/api/v1/organizations/current", response_model=OrganizationOut)
def current_organization(context: OrgContext = Depends(get_org_context)):
    return context.organization


@app.post("/api/v1/organizations", response_model=OrganizationOut, status_code=status.HTTP_201_CREATED)
def create_organization(
    name: str,
    context: OrgContext = Depends(require_roles(Role.admin)),
    db: Session = Depends(get_db),
):
    organization = Organization(name=name, slug=unique_slug(db, name, Organization))
    db.add(organization)
    db.flush()
    db.add(Membership(user_id=context.user.id, organization_id=organization.id, role=Role.admin))
    write_audit(
        db,
        organization_id=organization.id,
        user_id=context.user.id,
        action="organization.created",
        entity_type="organization",
        entity_id=organization.id,
    )
    db.commit()
    return organization


@app.post("/api/v1/organizations/{organization_id}/members", response_model=MemberOut)
def add_member(
    organization_id: str,
    payload: MemberCreate,
    context: OrgContext = Depends(require_roles(Role.admin)),
    db: Session = Depends(get_db),
):
    if context.organization_id != organization_id:
        raise HTTPException(status_code=403, detail="Kuruluş başlığı eşleşmiyor.")
    user = db.scalar(select(User).where(User.email == payload.email.lower()))
    if not user:
        raise HTTPException(status_code=404, detail="Kullanıcı önce kendi kuruluşuyla kayıt olmalıdır.")
    membership = db.scalar(
        select(Membership).where(
            Membership.user_id == user.id,
            Membership.organization_id == organization_id,
        )
    )
    if membership:
        membership.role = payload.role
        membership.notify_incidents = payload.notify_incidents
    else:
        enforce_limit(db, context.organization, "members")
        membership = Membership(
            user_id=user.id,
            organization_id=organization_id,
            role=payload.role,
            notify_incidents=payload.notify_incidents,
        )
        db.add(membership)
    db.flush()
    write_audit(
        db,
        organization_id=organization_id,
        user_id=context.user.id,
        action="membership.upserted",
        entity_type="membership",
        entity_id=membership.id,
        details={
            "member_user_id": user.id,
            "role": payload.role.value,
            "notify_incidents": payload.notify_incidents,
        },
    )
    db.commit()
    return MemberOut(
        user_id=user.id,
        email=user.email,
        role=membership.role,
        notify_incidents=membership.notify_incidents,
    )


@app.get("/api/v1/billing/usage", response_model=BillingUsageOut)
def billing_usage(context: OrgContext = Depends(get_org_context), db: Session = Depends(get_db)):
    return usage_snapshot(db, context.organization)


@app.get("/api/v1/locations", response_model=list[LocationOut])
def list_locations(context: OrgContext = Depends(get_org_context), db: Session = Depends(get_db)):
    return db.scalars(
        select(Location).where(Location.organization_id == context.organization_id).order_by(Location.name)
    ).all()


@app.post("/api/v1/locations", response_model=LocationOut, status_code=status.HTTP_201_CREATED)
def create_location(
    payload: LocationCreate,
    context: OrgContext = Depends(require_roles(Role.admin, Role.technician)),
    db: Session = Depends(get_db),
):
    enforce_limit(db, context.organization, "locations")
    duplicate = db.scalar(
        select(Location.id).where(
            Location.organization_id == context.organization_id,
            Location.name == payload.name,
        )
    )
    if duplicate:
        raise HTTPException(status_code=409, detail="Bu lokasyon zaten kayıtlı.")
    location = Location(organization_id=context.organization_id, **payload.model_dump())
    db.add(location)
    db.flush()
    write_audit(db, organization_id=context.organization_id, user_id=context.user.id, action="location.created", entity_type="location", entity_id=location.id)
    db.commit()
    return location


@app.get("/api/v1/critical-loads", response_model=list[CriticalLoadOut])
def list_loads(
    location_id: str | None = None,
    context: OrgContext = Depends(get_org_context),
    db: Session = Depends(get_db),
):
    query = select(CriticalLoad).where(CriticalLoad.organization_id == context.organization_id)
    if location_id:
        query = query.where(CriticalLoad.location_id == location_id)
    return db.scalars(query.order_by(CriticalLoad.priority, CriticalLoad.name)).all()


@app.post("/api/v1/critical-loads", response_model=CriticalLoadOut, status_code=status.HTTP_201_CREATED)
def create_load(
    payload: CriticalLoadCreate,
    context: OrgContext = Depends(require_roles(Role.admin, Role.technician)),
    db: Session = Depends(get_db),
):
    enforce_limit(db, context.organization, "critical_loads")
    location = db.scalar(select(Location).where(Location.id == payload.location_id, Location.organization_id == context.organization_id))
    if not location:
        raise HTTPException(status_code=404, detail="Lokasyon bulunamadı.")
    load = CriticalLoad(organization_id=context.organization_id, **payload.model_dump())
    db.add(load)
    db.flush()
    write_audit(db, organization_id=context.organization_id, user_id=context.user.id, action="critical_load.created", entity_type="critical_load", entity_id=load.id, details={"priority": load.priority.value})
    db.commit()
    return load


@app.get("/api/v1/assets", response_model=list[AssetOut])
def list_assets(context: OrgContext = Depends(get_org_context), db: Session = Depends(get_db)):
    return db.scalars(select(Asset).where(Asset.organization_id == context.organization_id).order_by(Asset.name)).all()


@app.post("/api/v1/assets", response_model=AssetOut, status_code=status.HTTP_201_CREATED)
def create_asset(
    payload: AssetCreate,
    context: OrgContext = Depends(require_roles(Role.admin, Role.technician)),
    db: Session = Depends(get_db),
):
    enforce_limit(db, context.organization, "assets")
    location = db.scalar(select(Location).where(Location.id == payload.location_id, Location.organization_id == context.organization_id))
    if not location:
        raise HTTPException(status_code=404, detail="Lokasyon bulunamadı.")
    asset = Asset(organization_id=context.organization_id, **payload.model_dump())
    db.add(asset)
    db.flush()
    write_audit(db, organization_id=context.organization_id, user_id=context.user.id, action="asset.created", entity_type="asset", entity_id=asset.id)
    db.commit()
    return asset


@app.post("/api/v1/assets/{asset_id}/tests", response_model=AssetTestOut)
def add_asset_test(
    asset_id: str,
    payload: AssetTestCreate,
    context: OrgContext = Depends(require_roles(Role.admin, Role.technician)),
    db: Session = Depends(get_db),
):
    asset = db.scalar(select(Asset).where(Asset.id == asset_id, Asset.organization_id == context.organization_id))
    if not asset:
        raise HTTPException(status_code=404, detail="Varlık bulunamadı.")
    tested_at = payload.tested_at or utcnow()
    test = AssetTest(
        organization_id=context.organization_id,
        asset_id=asset.id,
        result=payload.result,
        notes=payload.notes,
        tested_at=tested_at,
        created_by_user_id=context.user.id,
    )
    asset.last_test_at = tested_at
    db.add(test)
    db.flush()
    write_audit(db, organization_id=context.organization_id, user_id=context.user.id, action="asset_test.created", entity_type="asset_test", entity_id=test.id, details={"asset_id": asset.id, "result": test.result})
    db.commit()
    return test


@app.get("/api/v1/incidents", response_model=list[IncidentOut])
def list_incidents(context: OrgContext = Depends(get_org_context), db: Session = Depends(get_db)):
    return db.scalars(incident_query(context.organization_id).order_by(Incident.started_at.desc())).all()


@app.post("/api/v1/incidents", response_model=IncidentOut, status_code=status.HTTP_201_CREATED)
def create_incident(
    payload: IncidentCreate,
    context: OrgContext = Depends(require_roles(Role.admin, Role.technician)),
    db: Session = Depends(get_db),
):
    location = db.scalar(select(Location).where(Location.id == payload.location_id, Location.organization_id == context.organization_id))
    if not location:
        raise HTTPException(status_code=404, detail="Lokasyon bulunamadı.")
    incident = Incident(
        organization_id=context.organization_id,
        location_id=payload.location_id,
        kind=payload.kind,
        summary=payload.summary,
        created_by_user_id=context.user.id,
    )
    db.add(incident)
    db.flush()
    db.add_all(build_incident_tasks(db, organization_id=context.organization_id, incident_id=incident.id, location_id=incident.location_id))
    notification_count = queue_incident_notifications(
        db,
        organization=context.organization,
        incident=incident,
        action="Olay başlatıldı",
    )
    write_audit(db, organization_id=context.organization_id, user_id=context.user.id, action="incident.created", entity_type="incident", entity_id=incident.id, details={"kind": incident.kind, "notification_count": notification_count})
    db.commit()
    return db.scalar(incident_query(context.organization_id).where(Incident.id == incident.id))


@app.post("/api/v1/incidents/{incident_id}/tasks/{task_id}/complete", response_model=TaskOut)
def complete_task(
    incident_id: str,
    task_id: str,
    context: OrgContext = Depends(require_roles(Role.admin, Role.technician)),
    db: Session = Depends(get_db),
):
    task = db.scalar(select(IncidentTask).where(IncidentTask.id == task_id, IncidentTask.incident_id == incident_id, IncidentTask.organization_id == context.organization_id))
    if not task:
        raise HTTPException(status_code=404, detail="Görev bulunamadı.")
    task.status = TaskStatus.completed
    task.completed_at = utcnow()
    write_audit(db, organization_id=context.organization_id, user_id=context.user.id, action="incident_task.completed", entity_type="incident_task", entity_id=task.id, details={"incident_id": incident_id})
    db.commit()
    return task


@app.post("/api/v1/incidents/{incident_id}/close", response_model=IncidentOut)
def close_incident(
    incident_id: str,
    payload: CloseIncidentRequest,
    context: OrgContext = Depends(require_roles(Role.admin, Role.technician)),
    db: Session = Depends(get_db),
):
    incident = db.scalar(incident_query(context.organization_id).where(Incident.id == incident_id))
    if not incident:
        raise HTTPException(status_code=404, detail="Olay bulunamadı.")
    missing = [task.title for task in incident.tasks if task.is_required and task.status != TaskStatus.completed]
    if missing:
        raise HTTPException(status_code=409, detail={"message": "Zorunlu görevler tamamlanmadan olay kapatılamaz.", "missing_tasks": missing})
    incident.status = IncidentStatus.closed
    incident.ended_at = utcnow()
    if payload.closure_note:
        incident.summary = f"{incident.summary or ''}\nKapanış: {payload.closure_note}".strip()
    notification_count = queue_incident_notifications(
        db,
        organization=context.organization,
        incident=incident,
        action="Olay kapatıldı",
    )
    write_audit(db, organization_id=context.organization_id, user_id=context.user.id, action="incident.closed", entity_type="incident", entity_id=incident.id, details={"notification_count": notification_count})
    db.commit()
    return incident


@app.get("/api/v1/audit-logs", response_model=list[AuditOut])
def list_audit_logs(
    limit: int = 100,
    context: OrgContext = Depends(require_roles(Role.admin)),
    db: Session = Depends(get_db),
):
    safe_limit = min(max(limit, 1), 500)
    return db.scalars(select(AuditLog).where(AuditLog.organization_id == context.organization_id).order_by(AuditLog.created_at.desc()).limit(safe_limit)).all()


@app.get("/api/v1/privacy/me/export", response_model=PrivacyExportOut)
def export_my_data(user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> PrivacyExportOut:
    return PrivacyExportOut(data=user_export(db, user))


@app.post("/api/v1/privacy/me/delete-request", response_model=GenericMessage)
def delete_my_account(
    payload: AccountDeletionRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> GenericMessage:
    if not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Parola hatalı.")
    request_user_deletion(db, user)
    db.commit()
    return GenericMessage(message=f"Hesap silme talebi alındı; {settings.deletion_grace_days} gün sonra uygulanacak.")


@app.get("/api/v1/privacy/organization/export", response_model=PrivacyExportOut)
def export_organization_data(
    context: OrgContext = Depends(require_roles(Role.admin)),
    db: Session = Depends(get_db),
) -> PrivacyExportOut:
    write_audit(db, organization_id=context.organization_id, user_id=context.user.id, action="privacy.organization_exported", entity_type="organization", entity_id=context.organization_id)
    data = organization_export(db, context.organization)
    db.commit()
    return PrivacyExportOut(data=data)


@app.post("/api/v1/privacy/organization/delete-request", response_model=GenericMessage)
def delete_organization(
    payload: OrganizationDeletionRequest,
    context: OrgContext = Depends(require_roles(Role.admin)),
    db: Session = Depends(get_db),
) -> GenericMessage:
    if not verify_password(payload.password, context.user.password_hash):
        raise HTTPException(status_code=401, detail="Parola hatalı.")
    if payload.organization_name.strip() != context.organization.name:
        raise HTTPException(status_code=400, detail="Kuruluş adı doğrulaması eşleşmiyor.")
    write_audit(db, organization_id=context.organization_id, user_id=context.user.id, action="privacy.organization_deletion_requested", entity_type="organization", entity_id=context.organization_id)
    request_organization_deletion(db, context.organization)
    db.commit()
    return GenericMessage(message=f"Kuruluş silme talebi alındı; {settings.deletion_grace_days} gün sonra uygulanacak.")

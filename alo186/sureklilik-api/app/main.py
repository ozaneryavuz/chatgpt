from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload

from .audit import write_audit
from .config import settings
from .db import init_db
from .deps import OrgContext, get_current_user, get_db, get_org_context, require_roles
from .models import (
    Asset,
    AssetTest,
    AuditLog,
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
from .schemas import (
    AssetCreate,
    AssetOut,
    AssetTestCreate,
    AssetTestOut,
    AuditOut,
    AuthResponse,
    CloseIncidentRequest,
    CriticalLoadCreate,
    CriticalLoadOut,
    IncidentCreate,
    IncidentOut,
    LocationCreate,
    LocationOut,
    LoginRequest,
    MemberCreate,
    MemberOut,
    MembershipOut,
    OrganizationOut,
    RegisterRequest,
    TaskOut,
    UserOut,
)
from .security import create_access_token, hash_password, verify_password
from .service import build_incident_tasks, unique_slug, utcnow


@asynccontextmanager
async def lifespan(_app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="ALO186 Elektrik Sürekliliği API",
    version="0.2.0",
    description=(
        "Otel, site ve işletmeler için tenant izolasyonlu kritik yük, "
        "yedek kaynak, test ve kesinti olayı API temeli."
    ),
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=list(settings.allowed_origins),
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
    allow_headers=["Authorization", "Content-Type", "X-Organization-ID"],
)


def incident_query(organization_id: str):
    return (
        select(Incident)
        .options(selectinload(Incident.tasks))
        .where(Incident.organization_id == organization_id)
    )


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "version": app.version}


@app.post("/api/v1/auth/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest, db: Session = Depends(get_db)) -> AuthResponse:
    email = payload.email.lower()
    if db.scalar(select(User.id).where(User.email == email)):
        raise HTTPException(status_code=409, detail="Bu e-posta zaten kayıtlı.")
    user = User(email=email, password_hash=hash_password(payload.password))
    organization = Organization(
        name=payload.organization_name,
        slug=unique_slug(db, payload.organization_name, Organization),
    )
    membership = Membership(user=user, organization=organization, role=Role.admin)
    db.add_all([user, organization, membership])
    try:
        db.flush()
        write_audit(
            db,
            organization_id=organization.id,
            user_id=user.id,
            action="organization.created",
            entity_type="organization",
            entity_id=organization.id,
        )
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="Kayıt oluşturulamadı.") from exc
    return AuthResponse(
        access_token=create_access_token(user.id),
        user=UserOut.model_validate(user),
        organization=organization,
    )


@app.post("/api/v1/auth/login", response_model=AuthResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> AuthResponse:
    user = db.scalar(select(User).where(User.email == payload.email.lower()))
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="E-posta veya parola hatalı.")
    membership = db.scalar(select(Membership).where(Membership.user_id == user.id))
    if not membership:
        raise HTTPException(status_code=403, detail="Kuruluş üyeliği bulunamadı.")
    return AuthResponse(
        access_token=create_access_token(user.id),
        user=UserOut.model_validate(user),
        organization=membership.organization,
    )


@app.get("/api/v1/auth/me", response_model=UserOut)
def me(user: User = Depends(get_current_user)) -> User:
    return user


@app.get("/api/v1/auth/memberships", response_model=list[MembershipOut])
def memberships(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.scalars(select(Membership).where(Membership.user_id == user.id)).all()


@app.get("/api/v1/organizations/current", response_model=OrganizationOut)
def current_organization(
    context: OrgContext = Depends(get_org_context),
    db: Session = Depends(get_db),
):
    organization = db.get(Organization, context.organization_id)
    if not organization:
        raise HTTPException(status_code=404, detail="Kuruluş bulunamadı.")
    return organization


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
        if membership.role == Role.admin and payload.role != Role.admin:
            admin_count = db.scalar(
                select(func.count(Membership.id)).where(
                    Membership.organization_id == organization_id,
                    Membership.role == Role.admin,
                )
            ) or 0
            if admin_count <= 1:
                raise HTTPException(
                    status_code=409,
                    detail="Kuruluşun son yöneticisinin rolü düşürülemez.",
                )
        membership.role = payload.role
    else:
        membership = Membership(user_id=user.id, organization_id=organization_id, role=payload.role)
        db.add(membership)
    db.flush()
    write_audit(
        db,
        organization_id=organization_id,
        user_id=context.user.id,
        action="membership.upserted",
        entity_type="membership",
        entity_id=membership.id,
        details={"member_user_id": user.id, "role": payload.role.value},
    )
    db.commit()
    return MemberOut(user_id=user.id, email=user.email, role=membership.role)


@app.get("/api/v1/locations", response_model=list[LocationOut])
def list_locations(
    context: OrgContext = Depends(get_org_context),
    db: Session = Depends(get_db),
):
    return db.scalars(
        select(Location).where(Location.organization_id == context.organization_id).order_by(Location.name)
    ).all()


@app.post("/api/v1/locations", response_model=LocationOut, status_code=status.HTTP_201_CREATED)
def create_location(
    payload: LocationCreate,
    context: OrgContext = Depends(require_roles(Role.admin, Role.technician)),
    db: Session = Depends(get_db),
):
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
    if asset.last_test_at is None or tested_at > asset.last_test_at:
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
    write_audit(db, organization_id=context.organization_id, user_id=context.user.id, action="incident.created", entity_type="incident", entity_id=incident.id, details={"kind": incident.kind})
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
    if incident.status == IncidentStatus.closed:
        return incident
    missing = [task.title for task in incident.tasks if task.is_required and task.status != TaskStatus.completed]
    if missing:
        raise HTTPException(status_code=409, detail={"message": "Zorunlu görevler tamamlanmadan olay kapatılamaz.", "missing_tasks": missing})
    incident.status = IncidentStatus.closed
    incident.ended_at = utcnow()
    if payload.closure_note:
        incident.summary = f"{incident.summary or ''}\nKapanış: {payload.closure_note}".strip()
    write_audit(db, organization_id=context.organization_id, user_id=context.user.id, action="incident.closed", entity_type="incident", entity_id=incident.id)
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

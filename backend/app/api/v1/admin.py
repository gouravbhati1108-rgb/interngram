from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select

from app.core.audit import log_audit
from app.core.deps import CurrentUser, DbSession, require_csrf
from app.models import AuditLog, Company, Report, Review, User, VerificationDocument
from app.models.company import VerificationStatus
from app.models.report import ReportStatus
from app.models.review import ModerationStatus
from app.models.user import UserRole
from app.models.verification import DocumentStatus
from app.schemas.admin import ReportStatusUpdate, UserStatusUpdate, VerificationDecision
from app.schemas.review import ModerationUpdate
from app.services.notification import notify_review_moderation, notify_verification_decision
from app.services.ranking import recalculate_company_ranking

router = APIRouter(prefix="/admin", tags=["admin"])


def _require_admin(user: CurrentUser):
    if user.role != UserRole.admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")


@router.get("/users")
async def list_users(current_user: CurrentUser, db: DbSession):
    _require_admin(current_user)
    result = await db.execute(select(User).order_by(User.created_at.desc()))
    return [
        {"id": u.id, "email": u.email, "role": u.role.value, "is_active": u.is_active}
        for u in result.scalars().all()
    ]


@router.patch("/users/{user_id}", dependencies=[Depends(require_csrf)])
async def update_user_status(
    user_id: int, data: UserStatusUpdate, request: Request, current_user: CurrentUser, db: DbSession
):
    _require_admin(current_user)
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    user.is_active = data.is_active
    await log_audit(db, current_user.id, "user_status_update", f"user:{user_id}", ip=request.client.host if request.client else None)
    await db.flush()
    return {"id": user.id, "is_active": user.is_active}


@router.get("/companies/pending")
async def pending_companies(current_user: CurrentUser, db: DbSession):
    _require_admin(current_user)
    result = await db.execute(
        select(Company).where(Company.verification_status == VerificationStatus.pending)
    )
    return [
        {"id": c.id, "name": c.name, "slug": c.slug, "website": c.website}
        for c in result.scalars().all()
    ]


@router.patch("/companies/{company_id}/verify", dependencies=[Depends(require_csrf)])
async def verify_company(
    company_id: int, data: VerificationDecision, request: Request, current_user: CurrentUser, db: DbSession
):
    _require_admin(current_user)
    company = await db.get(Company, company_id)
    if not company:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found")
    company.verification_status = VerificationStatus(data.status)
    await log_audit(db, current_user.id, "company_verification", f"company:{company_id}", metadata={"status": data.status}, ip=request.client.host if request.client else None)
    await recalculate_company_ranking(db, company_id)
    await db.flush()
    return {"id": company.id, "status": company.verification_status.value}


@router.get("/verifications/pending")
async def pending_verifications(current_user: CurrentUser, db: DbSession):
    _require_admin(current_user)
    result = await db.execute(
        select(VerificationDocument).where(VerificationDocument.status == DocumentStatus.pending)
    )
    return [
        {
            "id": d.id,
            "student_id": d.student_id,
            "company_id": d.company_id,
            "doc_type": d.doc_type.value,
            "s3_key": d.s3_key,
        }
        for d in result.scalars().all()
    ]


@router.patch("/verifications/{doc_id}", dependencies=[Depends(require_csrf)])
async def review_verification(
    doc_id: int, data: VerificationDecision, request: Request, current_user: CurrentUser, db: DbSession
):
    _require_admin(current_user)
    doc = await db.get(VerificationDocument, doc_id)
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    doc.status = DocumentStatus(data.status)
    doc.reviewed_by = current_user.id
    doc.reviewed_at = datetime.now(timezone.utc)
    student = doc.student
    await notify_verification_decision(db, student.user_id, doc.id, doc.status.value)
    await log_audit(db, current_user.id, "verification_review", f"doc:{doc_id}", metadata={"status": data.status}, ip=request.client.host if request.client else None)
    await db.flush()
    return {"id": doc.id, "status": doc.status.value}


@router.get("/reviews/pending")
async def pending_reviews(current_user: CurrentUser, db: DbSession):
    _require_admin(current_user)
    result = await db.execute(select(Review).where(Review.moderation_status == ModerationStatus.pending))
    return [
        {"id": r.id, "company_id": r.company_id, "student_id": r.student_id, "text": r.text[:200]}
        for r in result.scalars().all()
    ]


@router.patch("/reviews/{review_id}", dependencies=[Depends(require_csrf)])
async def moderate_review(
    review_id: int, data: ModerationUpdate, request: Request, current_user: CurrentUser, db: DbSession
):
    _require_admin(current_user)
    review = await db.get(Review, review_id)
    if not review:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Review not found")
    review.moderation_status = ModerationStatus(data.status)
    student = review.student
    await notify_review_moderation(db, student.user_id, review.id, review.moderation_status.value)
    await recalculate_company_ranking(db, review.company_id)
    await log_audit(db, current_user.id, "review_moderation", f"review:{review_id}", metadata={"status": data.status}, ip=request.client.host if request.client else None)
    await db.flush()
    return {"id": review.id, "status": review.moderation_status.value}


@router.get("/reports")
async def list_reports(current_user: CurrentUser, db: DbSession):
    _require_admin(current_user)
    result = await db.execute(select(Report).where(Report.status == ReportStatus.pending))
    return [
        {
            "id": r.id,
            "target_type": r.target_type.value,
            "target_id": r.target_id,
            "reason": r.reason,
            "reporter_id": r.reporter_id,
        }
        for r in result.scalars().all()
    ]


@router.patch("/reports/{report_id}", dependencies=[Depends(require_csrf)])
async def resolve_report(
    report_id: int, data: ReportStatusUpdate, request: Request, current_user: CurrentUser, db: DbSession
):
    _require_admin(current_user)
    report = await db.get(Report, report_id)
    if not report:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found")
    report.status = ReportStatus(data.status)
    await log_audit(db, current_user.id, "report_resolution", f"report:{report_id}", metadata={"status": data.status}, ip=request.client.host if request.client else None)
    await db.flush()
    return {"id": report.id, "status": report.status.value}


@router.get("/audit-logs")
async def audit_logs(current_user: CurrentUser, db: DbSession):
    _require_admin(current_user)
    result = await db.execute(select(AuditLog).order_by(AuditLog.created_at.desc()).limit(100))
    return [
        {
            "id": a.id,
            "actor_id": a.actor_id,
            "action": a.action,
            "resource": a.resource,
            "metadata": a.metadata_,
            "ip": a.ip,
            "created_at": a.created_at.isoformat(),
        }
        for a in result.scalars().all()
    ]


@router.get("/rankings")
async def ranking_monitor(current_user: CurrentUser, db: DbSession):
    _require_admin(current_user)
    from app.models import Ranking

    result = await db.execute(select(Ranking).order_by(Ranking.composite_score.desc()).limit(50))
    return [
        {
            "company_id": r.company_id,
            "composite_score": r.composite_score,
            "is_provisional": r.is_provisional,
            "computed_at": r.computed_at.isoformat(),
        }
        for r in result.scalars().all()
    ]

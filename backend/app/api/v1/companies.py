from datetime import date

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select

from app.core.deps import CurrentUser, DbSession, require_csrf
from app.core.s3 import create_presigned_upload, generate_s3_key, validate_upload
from app.models import Application, Company, Internship, Review
from app.models.application import ApplicationStatus
from app.models.internship import InternshipMode, InternshipStatus
from app.models.review import ModerationStatus
from app.models.user import UserRole
from app.schemas.company import (
    AnalyticsResponse,
    ApplicantStatusUpdate,
    CompanyProfileResponse,
    CompanyProfileUpdate,
    InternshipCreate,
    InternshipResponse,
    InternshipUpdate,
    PresignedUploadRequest,
    PresignedUploadResponse,
)
from app.services.notification import notify_application_status

router = APIRouter(prefix="/companies", tags=["companies"])


def _require_company(user: CurrentUser) -> Company:
    if user.role != UserRole.company or not user.company:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Company access required")
    return user.company


@router.get("/me", response_model=CompanyProfileResponse)
async def get_company_profile(current_user: CurrentUser):
    return _require_company(current_user)


@router.patch("/me", response_model=CompanyProfileResponse, dependencies=[Depends(require_csrf)])
async def update_company_profile(data: CompanyProfileUpdate, current_user: CurrentUser, db: DbSession):
    company = _require_company(current_user)
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(company, field, value)
    await db.flush()
    return company


@router.post("/logo/upload-url", dependencies=[Depends(require_csrf)])
async def logo_upload_url(data: PresignedUploadRequest, current_user: CurrentUser):
    _require_company(current_user)
    try:
        validate_upload("logo", data.content_type, data.size)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    key = generate_s3_key("logo", current_user.id, data.filename)
    upload = create_presigned_upload(key, data.content_type)
    return {"upload": upload, "s3_key": key}


@router.post("/internships", response_model=InternshipResponse, dependencies=[Depends(require_csrf)])
async def create_internship(data: InternshipCreate, current_user: CurrentUser, db: DbSession):
    company = _require_company(current_user)
    deadline = date.fromisoformat(data.deadline) if data.deadline else None
    internship = Internship(
        company_id=company.id,
        title=data.title,
        description=data.description,
        location=data.location,
        mode=InternshipMode(data.mode),
        stipend=data.stipend,
        skills_required=data.skills_required,
        deadline=deadline,
        status=InternshipStatus.open,
    )
    db.add(internship)
    await db.flush()
    return InternshipResponse(
        **{c: getattr(internship, c) for c in InternshipResponse.model_fields if c != "company_name"},
        company_name=company.name,
        deadline=str(internship.deadline) if internship.deadline else None,
        mode=internship.mode.value,
        status=internship.status.value,
    )


@router.patch("/internships/{internship_id}", dependencies=[Depends(require_csrf)])
async def update_internship(
    internship_id: int, data: InternshipUpdate, current_user: CurrentUser, db: DbSession
):
    company = _require_company(current_user)
    internship = await db.get(Internship, internship_id)
    if not internship or internship.company_id != company.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Internship not found")
    updates = data.model_dump(exclude_unset=True)
    if "deadline" in updates and updates["deadline"]:
        updates["deadline"] = date.fromisoformat(updates["deadline"])
    if "mode" in updates:
        updates["mode"] = InternshipMode(updates["mode"])
    if "status" in updates:
        updates["status"] = InternshipStatus(updates["status"])
    for field, value in updates.items():
        setattr(internship, field, value)
    await db.flush()
    return {"id": internship.id, "status": internship.status.value}


@router.get("/internships", response_model=list[InternshipResponse])
async def list_company_internships(current_user: CurrentUser, db: DbSession):
    company = _require_company(current_user)
    result = await db.execute(select(Internship).where(Internship.company_id == company.id))
    internships = result.scalars().all()
    return [
        InternshipResponse(
            id=i.id,
            company_id=i.company_id,
            title=i.title,
            description=i.description,
            location=i.location,
            mode=i.mode.value,
            stipend=i.stipend,
            skills_required=i.skills_required,
            deadline=str(i.deadline) if i.deadline else None,
            status=i.status.value,
            company_name=company.name,
        )
        for i in internships
    ]


@router.get("/applications", dependencies=[Depends(require_csrf)])
async def list_applicants(current_user: CurrentUser, db: DbSession):
    company = _require_company(current_user)
    result = await db.execute(
        select(Application, Internship)
        .join(Internship)
        .where(Internship.company_id == company.id)
    )
    return [
        {
            "application_id": app.id,
            "internship_id": internship.id,
            "internship_title": internship.title,
            "student_id": app.student_id,
            "status": app.status.value,
            "applied_at": app.applied_at.isoformat(),
        }
        for app, internship in result.all()
    ]


@router.patch("/applications/{application_id}", dependencies=[Depends(require_csrf)])
async def update_applicant_status(
    application_id: int, data: ApplicantStatusUpdate, current_user: CurrentUser, db: DbSession
):
    company = _require_company(current_user)
    app = await db.get(Application, application_id)
    if not app:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Application not found")
    internship = await db.get(Internship, app.internship_id)
    if internship.company_id != company.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your applicant")

    app.status = ApplicationStatus(data.status)
    await db.flush()
    student = app.student
    await notify_application_status(db, student.user_id, app.id, app.status.value)
    return {"id": app.id, "status": app.status.value}


@router.get("/analytics", response_model=AnalyticsResponse)
async def company_analytics(current_user: CurrentUser, db: DbSession):
    company = _require_company(current_user)
    total_result = await db.execute(
        select(func.count(Application.id)).join(Internship).where(Internship.company_id == company.id)
    )
    total = total_result.scalar() or 0
    completed_result = await db.execute(
        select(func.count(Application.id))
        .join(Internship)
        .where(Internship.company_id == company.id, Application.status == ApplicationStatus.completed)
    )
    completed = completed_result.scalar() or 0
    accepted_result = await db.execute(
        select(func.count(Application.id))
        .join(Internship)
        .where(Internship.company_id == company.id, Application.status == ApplicationStatus.accepted)
    )
    accepted = accepted_result.scalar() or 0
    reviews_result = await db.execute(
        select(Review).where(
            Review.company_id == company.id,
            Review.moderation_status == ModerationStatus.approved,
        )
    )
    reviews = list(reviews_result.scalars().all())
    return AnalyticsResponse(
        total_applications=total,
        completion_rate=completed / total if total else 0,
        ppo_rate=accepted / completed if completed else 0,
        avg_learning=sum(r.learning_score for r in reviews) / len(reviews) if reviews else 0,
        avg_mentorship=sum(r.mentorship_score for r in reviews) / len(reviews) if reviews else 0,
    )

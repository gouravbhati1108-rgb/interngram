from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select

from app.core.deps import CurrentUser, DbSession, require_csrf
from app.core.s3 import create_presigned_upload, generate_s3_key, validate_upload
from app.models.application import Application, ApplicationStatus
from app.models.internship import Internship, InternshipStatus
from app.models.user import UserRole
from app.models.verification import DocumentStatus, DocumentType, VerificationDocument
from app.schemas.student import (
    ApplicationResponse,
    PresignedUploadRequest,
    PresignedUploadResponse,
    StudentProfileResponse,
    StudentProfileUpdate,
    VerificationDocRequest,
)
from app.services.notification import notify_application_status

router = APIRouter(prefix="/students", tags=["students"])


def _require_student(user: CurrentUser):
    if user.role != UserRole.student or not user.student:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Student access required")


@router.get("/me", response_model=StudentProfileResponse)
async def get_profile(current_user: CurrentUser):
    _require_student(current_user)
    return current_user.student


@router.patch("/me", response_model=StudentProfileResponse, dependencies=[Depends(require_csrf)])
async def update_profile(data: StudentProfileUpdate, current_user: CurrentUser, db: DbSession):
    _require_student(current_user)
    student = current_user.student
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(student, field, value)
    await db.flush()
    return student


@router.post("/resume/upload-url", response_model=PresignedUploadResponse, dependencies=[Depends(require_csrf)])
async def resume_upload_url(data: PresignedUploadRequest, current_user: CurrentUser):
    _require_student(current_user)
    try:
        validate_upload("resume", data.content_type, data.size)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    key = generate_s3_key("resume", current_user.id, data.filename)
    upload = create_presigned_upload(key, data.content_type)
    return PresignedUploadResponse(upload=upload, s3_key=key)


@router.post("/resume/confirm", response_model=StudentProfileResponse, dependencies=[Depends(require_csrf)])
async def confirm_resume(s3_key: str, current_user: CurrentUser, db: DbSession):
    _require_student(current_user)
    current_user.student.resume_s3_key = s3_key
    await db.flush()
    return current_user.student


@router.get("/applications", response_model=list[ApplicationResponse])
async def list_applications(current_user: CurrentUser, db: DbSession):
    _require_student(current_user)
    result = await db.execute(
        select(Application).where(Application.student_id == current_user.student.id)
    )
    return list(result.scalars().all())


@router.post("/applications/{internship_id}", response_model=ApplicationResponse, dependencies=[Depends(require_csrf)])
async def apply_internship(internship_id: int, current_user: CurrentUser, db: DbSession):
    _require_student(current_user)
    internship = await db.get(Internship, internship_id)
    if not internship or internship.status != InternshipStatus.open:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Internship not available")

    existing = await db.execute(
        select(Application).where(
            Application.student_id == current_user.student.id,
            Application.internship_id == internship_id,
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Already applied")

    app = Application(student_id=current_user.student.id, internship_id=internship_id)
    db.add(app)
    await db.flush()
    return app


@router.post("/verification/upload-url", response_model=PresignedUploadResponse, dependencies=[Depends(require_csrf)])
async def verification_upload_url(data: PresignedUploadRequest, current_user: CurrentUser):
    _require_student(current_user)
    try:
        validate_upload("verification", data.content_type, data.size)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    key = generate_s3_key("verification", current_user.id, data.filename)
    upload = create_presigned_upload(key, data.content_type)
    return PresignedUploadResponse(upload=upload, s3_key=key)


@router.post("/verification", dependencies=[Depends(require_csrf)])
async def submit_verification(data: VerificationDocRequest, current_user: CurrentUser, db: DbSession):
    _require_student(current_user)
    try:
        doc_type = DocumentType(data.doc_type)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid document type")

    doc = VerificationDocument(
        student_id=current_user.student.id,
        company_id=data.company_id,
        doc_type=doc_type,
        s3_key=data.s3_key,
        status=DocumentStatus.pending,
    )
    db.add(doc)
    await db.flush()
    return {"id": doc.id, "status": doc.status.value}

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.deps import CurrentUser, DbSession, require_csrf
from app.models import Company, Review, Student
from app.models.user import UserRole
from app.schemas.review import ReviewCreate, ReviewResponse
from app.services.review import create_review, get_company_reviews, student_can_review

router = APIRouter(prefix="/reviews", tags=["reviews"])


@router.get("/company/{company_id}", response_model=list[ReviewResponse])
async def list_company_reviews(company_id: int, db: DbSession):
    reviews = await get_company_reviews(db, company_id)
    result = await db.execute(select(Student).where(Student.id.in_([r.student_id for r in reviews])))
    students = {s.id: s.name for s in result.scalars().all()}
    return [
        ReviewResponse(
            id=r.id,
            company_id=r.company_id,
            internship_id=r.internship_id,
            learning_score=r.learning_score,
            mentorship_score=r.mentorship_score,
            work_env_score=r.work_env_score,
            project_quality_score=r.project_quality_score,
            recommendation_score=r.recommendation_score,
            text=r.text,
            moderation_status=r.moderation_status.value,
            created_at=r.created_at,
            student_name=students.get(r.student_id),
        )
        for r in reviews
    ]


@router.post("", response_model=ReviewResponse, dependencies=[Depends(require_csrf)])
async def submit_review(data: ReviewCreate, current_user: CurrentUser, db: DbSession):
    if current_user.role != UserRole.student or not current_user.student:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Students only")
    try:
        review = await create_review(db, current_user.student.id, data.model_dump())
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return ReviewResponse(
        id=review.id,
        company_id=review.company_id,
        internship_id=review.internship_id,
        learning_score=review.learning_score,
        mentorship_score=review.mentorship_score,
        work_env_score=review.work_env_score,
        project_quality_score=review.project_quality_score,
        recommendation_score=review.recommendation_score,
        text=review.text,
        moderation_status=review.moderation_status.value,
        created_at=review.created_at,
        student_name=current_user.student.name,
    )


@router.get("/eligibility/{company_id}")
async def check_eligibility(company_id: int, current_user: CurrentUser, db: DbSession):
    if current_user.role != UserRole.student or not current_user.student:
        return {"eligible": False}
    eligible = await student_can_review(db, current_user.student.id, company_id)
    return {"eligible": eligible}

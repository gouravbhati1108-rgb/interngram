from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.redis_client import cache_delete_pattern
from app.core.sanitize import sanitize_html
from app.models import Application, Company, Internship, Review, VerificationDocument
from app.models.application import ApplicationStatus
from app.models.review import ModerationStatus
from app.models.verification import DocumentStatus


async def student_can_review(db: AsyncSession, student_id: int, company_id: int) -> bool:
    result = await db.execute(
        select(VerificationDocument).where(
            VerificationDocument.student_id == student_id,
            VerificationDocument.company_id == company_id,
            VerificationDocument.status == DocumentStatus.approved,
        )
    )
    return result.scalar_one_or_none() is not None


async def create_review(db: AsyncSession, student_id: int, data: dict) -> Review:
    if not await student_can_review(db, student_id, data["company_id"]):
        raise PermissionError("Not a verified intern for this company")

    existing = await db.execute(
        select(Review).where(
            Review.student_id == student_id,
            Review.company_id == data["company_id"],
            Review.internship_id == data["internship_id"],
        )
    )
    if existing.scalar_one_or_none():
        raise ValueError("Review already submitted for this internship")

    review = Review(
        student_id=student_id,
        company_id=data["company_id"],
        internship_id=data["internship_id"],
        learning_score=data["learning_score"],
        mentorship_score=data["mentorship_score"],
        work_env_score=data["work_env_score"],
        project_quality_score=data["project_quality_score"],
        recommendation_score=data["recommendation_score"],
        text=sanitize_html(data["text"]),
        is_verified=True,
        moderation_status=ModerationStatus.pending,
    )
    db.add(review)
    await db.flush()
    await cache_delete_pattern("rankings:*")
    return review


async def get_company_reviews(db: AsyncSession, company_id: int, include_pending: bool = False) -> list[Review]:
    query = select(Review).where(Review.company_id == company_id)
    if not include_pending:
        query = query.where(Review.moderation_status == ModerationStatus.approved)
    result = await db.execute(query.order_by(Review.created_at.desc()))
    return list(result.scalars().all())


async def compute_company_metrics(db: AsyncSession, company_id: int) -> dict:
    apps_result = await db.execute(
        select(func.count(Application.id)).join(Internship).where(Internship.company_id == company_id)
    )
    total_apps = apps_result.scalar() or 0

    completed_result = await db.execute(
        select(func.count(Application.id))
        .join(Internship)
        .where(Internship.company_id == company_id, Application.status == ApplicationStatus.completed)
    )
    completed = completed_result.scalar() or 0

    reviews_result = await db.execute(
        select(Review).where(
            Review.company_id == company_id,
            Review.moderation_status == ModerationStatus.approved,
        )
    )
    reviews = list(reviews_result.scalars().all())

    complaints_result = await db.execute(
        select(func.count()).select_from(Review).where(
            Review.company_id == company_id,
            Review.moderation_status == ModerationStatus.flagged,
        )
    )
    complaints = complaints_result.scalar() or 0

    company_result = await db.execute(select(Company).where(Company.id == company_id))
    company = company_result.scalar_one()

    avg_learning = sum(r.learning_score for r in reviews) / len(reviews) if reviews else 0
    avg_mentorship = sum(r.mentorship_score for r in reviews) / len(reviews) if reviews else 0
    avg_recommendation = sum(r.recommendation_score for r in reviews) / len(reviews) if reviews else 0

    completion_rate = completed / total_apps if total_apps else 0
    ppo_rate = 0.0  # tracked via future placement field; placeholder from accepted/completed ratio
    accepted_result = await db.execute(
        select(func.count(Application.id))
        .join(Internship)
        .where(Internship.company_id == company_id, Application.status == ApplicationStatus.accepted)
    )
    accepted = accepted_result.scalar() or 0
    if completed:
        ppo_rate = accepted / completed

    trust_score = 1.0 if company.verification_status.value == "verified" else 0.5
    complaint_rate = min(complaints / max(len(reviews), 1), 1.0)

    return {
        "verified_review_count": len(reviews),
        "verified_review_avg": avg_recommendation / 5 if reviews else 0,
        "completion_rate": completion_rate,
        "ppo_conversion_rate": ppo_rate,
        "learning_score": avg_learning / 5 if reviews else 0,
        "mentorship_score": avg_mentorship / 5 if reviews else 0,
        "trust_score": trust_score,
        "complaint_rate_penalty": complaint_rate,
    }

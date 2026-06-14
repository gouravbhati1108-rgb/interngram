from fastapi import APIRouter, HTTPException, Query, status
from sqlalchemy import or_, select
from sqlalchemy.orm import selectinload

from app.core.deps import DbSession
from app.core.redis_client import cache_delete_pattern, cache_get, cache_set
from app.models import Company, Internship
from app.models.internship import InternshipStatus
from app.schemas.company import InternshipResponse

router = APIRouter(prefix="/internships", tags=["internships"])


@router.get("", response_model=list[InternshipResponse])
async def list_internships(
    db: DbSession,
    q: str | None = None,
    location: str | None = None,
    min_stipend: int | None = None,
    skill: str | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    cache_key = f"internships:{q}:{location}:{min_stipend}:{skill}:{page}:{page_size}"
    cached = await cache_get(cache_key)
    if cached:
        return cached

    query = (
        select(Internship, Company)
        .join(Company)
        .where(Internship.status == InternshipStatus.open)
        .options(selectinload(Internship.company))
    )
    if q:
        query = query.where(
            or_(Internship.title.ilike(f"%{q}%"), Internship.description.ilike(f"%{q}%"))
        )
    if location:
        query = query.where(Internship.location.ilike(f"%{location}%"))
    if min_stipend:
        query = query.where(Internship.stipend >= min_stipend)
    if skill:
        query = query.where(Internship.skills_required.contains([skill]))

    offset = (page - 1) * page_size
    result = await db.execute(query.offset(offset).limit(page_size).order_by(Internship.created_at.desc()))
    items = [
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
            company_name=c.name,
        )
        for i, c in result.all()
    ]
    await cache_set(cache_key, items, ttl=60)
    return items


@router.get("/{internship_id}", response_model=InternshipResponse)
async def get_internship(internship_id: int, db: DbSession):
    result = await db.execute(
        select(Internship, Company).join(Company).where(Internship.id == internship_id)
    )
    row = result.first()
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Internship not found")
    internship, company = row
    return InternshipResponse(
        id=internship.id,
        company_id=internship.company_id,
        title=internship.title,
        description=internship.description,
        location=internship.location,
        mode=internship.mode.value,
        stipend=internship.stipend,
        skills_required=internship.skills_required,
        deadline=str(internship.deadline) if internship.deadline else None,
        status=internship.status.value,
        company_name=company.name,
    )

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select

from app.core.deps import DbSession
from app.models import Company
from app.schemas.company import CompanyProfileResponse

router = APIRouter(prefix="/public", tags=["public"])


@router.get("/companies/{slug}", response_model=CompanyProfileResponse)
async def get_company_public(slug: str, db: DbSession):
    result = await db.execute(select(Company).where(Company.slug == slug))
    company = result.scalar_one_or_none()
    if not company:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found")
    return CompanyProfileResponse(
        id=company.id,
        user_id=company.user_id,
        name=company.name,
        slug=company.slug,
        logo_s3_key=company.logo_s3_key,
        verification_status=company.verification_status.value,
        description=company.description,
        website=company.website,
    )

from fastapi import APIRouter, Query

from app.core.deps import DbSession
from app.schemas.ranking import RankingResponse
from app.services.ranking import get_leaderboard, recalculate_company_ranking

router = APIRouter(prefix="/rankings", tags=["rankings"])


@router.get("", response_model=list[RankingResponse])
async def leaderboard(
    db: DbSession,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    items, _ = await get_leaderboard(db, page, page_size)
    return [RankingResponse(**item) for item in items]


@router.get("/company/{company_id}")
async def company_ranking(company_id: int, db: DbSession):
    ranking = await recalculate_company_ranking(db, company_id)
    return {
        "company_id": ranking.company_id,
        "composite_score": ranking.composite_score,
        "factor_scores": ranking.factor_scores,
        "is_provisional": ranking.is_provisional,
        "computed_at": ranking.computed_at.isoformat(),
    }

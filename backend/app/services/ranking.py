from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.redis_client import cache_delete_pattern, cache_get, cache_set
from app.models import Company, Ranking
from app.services.review import compute_company_metrics

WEIGHTS = {
    "verified_review_avg": 0.25,
    "completion_rate": 0.15,
    "ppo_conversion_rate": 0.15,
    "learning_score": 0.15,
    "mentorship_score": 0.10,
    "trust_score": 0.10,
    "complaint_rate_penalty": -0.10,
}

PROVISIONAL_THRESHOLD = 3
PROVISIONAL_DAMPENING = 0.7


def calculate_composite_score(factors: dict, is_provisional: bool) -> float:
    score = sum(factors.get(k, 0) * w for k, w in WEIGHTS.items()) * 100
    if is_provisional:
        score *= PROVISIONAL_DAMPENING
    return round(max(0, min(100, score)), 2)


async def recalculate_company_ranking(db: AsyncSession, company_id: int) -> Ranking:
    metrics = await compute_company_metrics(db, company_id)
    is_provisional = metrics["verified_review_count"] < PROVISIONAL_THRESHOLD
    composite = calculate_composite_score(metrics, is_provisional)

    result = await db.execute(select(Ranking).where(Ranking.company_id == company_id))
    ranking = result.scalar_one_or_none()
    if ranking:
        ranking.composite_score = composite
        ranking.factor_scores = metrics
        ranking.is_provisional = is_provisional
        ranking.computed_at = datetime.now(timezone.utc)
    else:
        ranking = Ranking(
            company_id=company_id,
            composite_score=composite,
            factor_scores=metrics,
            is_provisional=is_provisional,
        )
        db.add(ranking)
    await db.flush()
    await cache_delete_pattern("rankings:*")
    return ranking


async def recalculate_all_rankings(db: AsyncSession) -> int:
    result = await db.execute(select(Company.id))
    company_ids = list(result.scalars().all())
    for cid in company_ids:
        await recalculate_company_ranking(db, cid)
    return len(company_ids)


async def get_leaderboard(db: AsyncSession, page: int = 1, page_size: int = 20) -> tuple[list[dict], int]:
    cache_key = f"rankings:page:{page}:size:{page_size}"
    cached = await cache_get(cache_key)
    if cached:
        return cached["items"], cached["total"]

    count_result = await db.execute(select(Ranking))
    total = len(list(count_result.scalars().all()))

    offset = (page - 1) * page_size
    result = await db.execute(
        select(Ranking, Company)
        .join(Company, Ranking.company_id == Company.id)
        .order_by(Ranking.composite_score.desc())
        .offset(offset)
        .limit(page_size)
    )
    items = []
    for ranking, company in result.all():
        items.append(
            {
                "company_id": company.id,
                "company_name": company.name,
                "company_slug": company.slug,
                "composite_score": ranking.composite_score,
                "factor_scores": ranking.factor_scores,
                "is_provisional": ranking.is_provisional,
                "computed_at": ranking.computed_at.isoformat(),
            }
        )
    await cache_set(cache_key, {"items": items, "total": total}, ttl=300)
    return items, total

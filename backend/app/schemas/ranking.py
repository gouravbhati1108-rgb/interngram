from datetime import datetime

from pydantic import BaseModel


class RankingResponse(BaseModel):
    company_id: int
    company_name: str
    company_slug: str
    composite_score: float
    factor_scores: dict
    is_provisional: bool
    computed_at: datetime | str

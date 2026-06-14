from datetime import datetime

from pydantic import BaseModel, Field


class RankingResponse(BaseModel):
    company_id: int
    company_name: str
    company_slug: str
    composite_score: float
    factor_scores: dict
    is_provisional: bool
    computed_at: datetime


class PostCreate(BaseModel):
    title: str = Field(min_length=3, max_length=255)
    body: str = Field(min_length=10)


class CommentCreate(BaseModel):
    body: str = Field(min_length=1)
    parent_id: int | None = None


class PostResponse(BaseModel):
    id: int
    company_id: int
    author_id: int
    title: str
    body: str
    is_pinned: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class CommentResponse(BaseModel):
    id: int
    post_id: int
    author_id: int
    body: str
    parent_id: int | None
    created_at: datetime

    model_config = {"from_attributes": True}


class ReportCreate(BaseModel):
    target_type: str
    target_id: int
    reason: str = Field(min_length=10)

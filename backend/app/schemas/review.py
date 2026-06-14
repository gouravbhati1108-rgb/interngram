from datetime import datetime

from pydantic import BaseModel, Field


class ReviewCreate(BaseModel):
    company_id: int
    internship_id: int
    learning_score: int = Field(ge=1, le=5)
    mentorship_score: int = Field(ge=1, le=5)
    work_env_score: int = Field(ge=1, le=5)
    project_quality_score: int = Field(ge=1, le=5)
    recommendation_score: int = Field(ge=1, le=5)
    text: str = Field(min_length=20, max_length=5000)


class ReviewResponse(BaseModel):
    id: int
    company_id: int
    internship_id: int
    learning_score: int
    mentorship_score: int
    work_env_score: int
    project_quality_score: int
    recommendation_score: int
    text: str
    moderation_status: str
    created_at: datetime
    student_name: str | None = None

    model_config = {"from_attributes": True}


class ModerationUpdate(BaseModel):
    status: str

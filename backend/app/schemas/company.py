from pydantic import BaseModel, Field


class CompanyProfileUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    website: str | None = None


class CompanyProfileResponse(BaseModel):
    id: int
    user_id: int
    name: str
    slug: str
    logo_s3_key: str | None
    verification_status: str
    description: str | None
    website: str | None

    model_config = {"from_attributes": True}


class InternshipCreate(BaseModel):
    title: str = Field(min_length=3)
    description: str = Field(min_length=10)
    location: str | None = None
    mode: str = "remote"
    stipend: int | None = None
    skills_required: list[str] = []
    deadline: str | None = None


class InternshipUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    location: str | None = None
    mode: str | None = None
    stipend: int | None = None
    skills_required: list[str] | None = None
    deadline: str | None = None
    status: str | None = None


class InternshipResponse(BaseModel):
    id: int
    company_id: int
    title: str
    description: str
    location: str | None
    mode: str
    stipend: int | None
    skills_required: list[str]
    deadline: str | None
    status: str
    company_name: str | None = None

    model_config = {"from_attributes": True}


class PresignedUploadRequest(BaseModel):
    filename: str
    content_type: str
    size: int


class PresignedUploadResponse(BaseModel):
    upload: dict
    s3_key: str


class ApplicantStatusUpdate(BaseModel):
    status: str


class AnalyticsResponse(BaseModel):
    total_applications: int
    completion_rate: float
    ppo_rate: float
    avg_learning: float
    avg_mentorship: float

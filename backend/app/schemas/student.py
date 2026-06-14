from datetime import datetime

from pydantic import BaseModel, Field


class StudentProfileUpdate(BaseModel):
    name: str | None = None
    college: str | None = None
    graduation_year: int | None = None
    skills: list[str] | None = None


class StudentProfileResponse(BaseModel):
    id: int
    user_id: int
    name: str
    college: str | None
    graduation_year: int | None
    skills: list[str]
    resume_s3_key: str | None

    model_config = {"from_attributes": True}


class PresignedUploadRequest(BaseModel):
    filename: str
    content_type: str
    size: int


class PresignedUploadResponse(BaseModel):
    upload: dict
    s3_key: str


class VerificationDocRequest(BaseModel):
    company_id: int
    doc_type: str
    s3_key: str


class ApplicationResponse(BaseModel):
    id: int
    internship_id: int
    status: str
    applied_at: datetime | None = None

    model_config = {"from_attributes": True}

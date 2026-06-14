from pydantic import BaseModel


class UserStatusUpdate(BaseModel):
    is_active: bool


class VerificationDecision(BaseModel):
    status: str
    reason: str | None = None


class ReportStatusUpdate(BaseModel):
    status: str

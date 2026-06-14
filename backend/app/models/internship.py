import enum
from datetime import date, datetime

from typing import Optional

from sqlalchemy import Date, DateTime, Enum, ForeignKey, Integer, String, Text, func
from sqlalchemy import JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class InternshipMode(str, enum.Enum):
    remote = "remote"
    onsite = "onsite"
    hybrid = "hybrid"


class InternshipStatus(str, enum.Enum):
    open = "open"
    closed = "closed"
    draft = "draft"


class Internship(Base):
    __tablename__ = "internships"

    id: Mapped[int] = mapped_column(primary_key=True)
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id", ondelete="CASCADE"), index=True)
    title: Mapped[str] = mapped_column(String(255), index=True)
    description: Mapped[str] = mapped_column(Text)
    location: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)
    mode: Mapped[InternshipMode] = mapped_column(Enum(InternshipMode), default=InternshipMode.remote)
    stipend: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, index=True)
    skills_required: Mapped[list] = mapped_column(JSON, default=list)
    deadline: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    status: Mapped[InternshipStatus] = mapped_column(Enum(InternshipStatus), default=InternshipStatus.open, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    company = relationship("Company", back_populates="internships")
    applications = relationship("Application", back_populates="internship")
    reviews = relationship("Review", back_populates="internship")

import pytest
from httpx import AsyncClient

from app.models import Company, Internship, Student, User, VerificationDocument
from app.models.company import VerificationStatus
from app.models.internship import InternshipStatus
from app.models.user import UserRole
from app.models.verification import DocumentStatus, DocumentType
from app.core.security import hash_password


@pytest.mark.asyncio
async def test_review_requires_verification(client: AsyncClient, db_session):
    user = User(email="s@test.com", password_hash=hash_password("pass"), role=UserRole.student)
    db_session.add(user)
    await db_session.flush()
    student = Student(user_id=user.id, name="S")
    db_session.add(student)

    cuser = User(email="c@test.com", password_hash=hash_password("pass"), role=UserRole.company)
    db_session.add(cuser)
    await db_session.flush()
    company = Company(user_id=cuser.id, name="Co", slug="co", verification_status=VerificationStatus.verified)
    db_session.add(company)
    await db_session.flush()

    from app.models.internship import Internship, InternshipMode
    internship = Internship(
        company_id=company.id, title="Intern", description="Desc", mode=InternshipMode.remote, status=InternshipStatus.open
    )
    db_session.add(internship)
    await db_session.commit()

    login = await client.post("/api/v1/auth/login", json={"email": "s@test.com", "password": "pass"})
    token = login.json()["access_token"]

    response = await client.post(
        "/api/v1/reviews",
        headers={"Authorization": f"Bearer {token}", "X-CSRF-Token": login.cookies.get("csrf_token", "test")},
        json={
            "company_id": company.id,
            "internship_id": internship.id,
            "learning_score": 5,
            "mentorship_score": 4,
            "work_env_score": 4,
            "project_quality_score": 5,
            "recommendation_score": 5,
            "text": "Great learning experience overall with strong mentorship.",
        },
    )
    assert response.status_code == 403

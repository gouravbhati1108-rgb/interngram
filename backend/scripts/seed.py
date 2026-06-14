import asyncio
import sys
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlalchemy import select

from app.core.database import AsyncSessionLocal
from app.core.security import hash_password
from app.models import Application, Company, Internship, Review, Student, User
from app.models.application import ApplicationStatus
from app.models.company import VerificationStatus
from app.models.internship import InternshipMode, InternshipStatus
from app.models.review import ModerationStatus
from app.models.user import UserRole
from app.services.ranking import recalculate_all_rankings


async def seed():
    async with AsyncSessionLocal() as db:
        existing = await db.execute(select(User).where(User.email == "admin@interngram.com"))
        if existing.scalar_one_or_none():
            print("Seed data already exists, skipping.")
            return

        admin = User(
            email="admin@interngram.com",
            password_hash=hash_password("AdminPass123!"),
            role=UserRole.admin,
            mfa_enabled=False,
        )
        db.add(admin)

        for i in range(1, 6):
            user = User(
                email=f"student{i}@test.com",
                password_hash=hash_password("StudentPass123!"),
                role=UserRole.student,
            )
            db.add(user)
            await db.flush()
            db.add(Student(user_id=user.id, name=f"Student {i}", college=f"IIT Test {i}", skills=["Python", "React"]))

        companies = []
        for i in range(1, 4):
            user = User(
                email=f"company{i}@test.com",
                password_hash=hash_password("CompanyPass123!"),
                role=UserRole.company,
            )
            db.add(user)
            await db.flush()
            company = Company(
                user_id=user.id,
                name=f"TechCorp {i}",
                slug=f"techcorp-{i}",
                verification_status=VerificationStatus.verified,
                description=f"Leading tech company #{i}",
                website=f"https://techcorp{i}.example.com",
            )
            db.add(company)
            companies.append(company)

        await db.flush()

        internships = []
        for company in companies:
            internship = Internship(
                company_id=company.id,
                title=f"Software Engineering Intern at {company.name}",
                description="Build real products with mentorship from senior engineers.",
                location="Bangalore",
                mode=InternshipMode.hybrid,
                stipend=25000 + company.id * 5000,
                skills_required=["Python", "JavaScript"],
                deadline=date.today() + timedelta(days=60),
                status=InternshipStatus.open,
            )
            db.add(internship)
            internships.append(internship)

        await db.flush()

        students_result = await db.execute(select(Student))
        students = list(students_result.scalars().all())

        for idx, student in enumerate(students[:3]):
            app = Application(
                student_id=student.id,
                internship_id=internships[idx % len(internships)].id,
                status=ApplicationStatus.completed,
            )
            db.add(app)

        await db.flush()
        await recalculate_all_rankings(db)
        await db.commit()
        print("Seed complete: 1 admin, 5 students, 3 companies, 3 internships")


if __name__ == "__main__":
    asyncio.run(seed())

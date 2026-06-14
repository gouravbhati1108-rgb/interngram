import re
import secrets

import pyotp
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_access_token, create_refresh_token, hash_password, verify_password
from app.models import Company, Student, User
from app.models.company import VerificationStatus
from app.models.user import UserRole


def slugify(name: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    return slug or secrets.token_hex(4)


async def register_user(db: AsyncSession, email: str, password: str, role: UserRole, name: str) -> User:
    existing = await db.execute(select(User).where(User.email == email))
    if existing.scalar_one_or_none():
        raise ValueError("Email already registered")

    user = User(email=email, password_hash=hash_password(password), role=role)
    db.add(user)
    await db.flush()

    if role == UserRole.student:
        db.add(Student(user_id=user.id, name=name))
    elif role == UserRole.company:
        base_slug = slugify(name)
        slug = base_slug
        counter = 1
        while True:
            result = await db.execute(select(Company).where(Company.slug == slug))
            if not result.scalar_one_or_none():
                break
            slug = f"{base_slug}-{counter}"
            counter += 1
        db.add(
            Company(
                user_id=user.id,
                name=name,
                slug=slug,
                verification_status=VerificationStatus.pending,
            )
        )
    elif role == UserRole.admin:
        secret = pyotp.random_base32()
        user.mfa_secret = secret
        user.mfa_enabled = True

    await db.flush()
    return user


async def authenticate_user(db: AsyncSession, email: str, password: str) -> User | None:
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    if not user or not verify_password(password, user.password_hash):
        return None
    return user


def build_tokens(user: User, mfa_pending: bool = False) -> tuple[str, str]:
    extra = {"role": user.role.value}
    if user.role == UserRole.admin and mfa_pending:
        extra["mfa_pending"] = True
    access = create_access_token(str(user.id), extra)
    refresh = create_refresh_token(str(user.id))
    return access, refresh


def verify_mfa_code(user: User, code: str) -> bool:
    if not user.mfa_secret:
        return False
    totp = pyotp.TOTP(user.mfa_secret)
    return totp.verify(code, valid_window=1)


def get_mfa_provisioning_uri(user: User) -> str:
    totp = pyotp.TOTP(user.mfa_secret)
    return totp.provisioning_uri(name=user.email, issuer_name="Interngram")

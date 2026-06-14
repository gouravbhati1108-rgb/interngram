from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy import select

from app.core.audit import log_audit
from app.core.deps import DbSession, csrf_cookie_value, generate_csrf_token
from app.core.security import verify_token
from app.models import User
from app.models.user import UserRole
from app.schemas.common import LoginRequest, MessageResponse, MfaVerifyRequest, RegisterRequest, TokenResponse, UserResponse
from app.services import auth as auth_service

router = APIRouter(prefix="/auth", tags=["auth"])
limiter = Limiter(key_func=get_remote_address)


def _set_auth_cookies(response: Response, access: str, refresh: str, csrf: str) -> None:
    response.set_cookie("access_token", access, httponly=True, samesite="lax", max_age=900)
    response.set_cookie("refresh_token", refresh, httponly=True, samesite="lax", max_age=604800)
    response.set_cookie("csrf_token", csrf, httponly=False, samesite="lax", max_age=604800)


@router.post("/register", response_model=UserResponse)
@limiter.limit("5/minute")
async def register(request: Request, data: RegisterRequest, db: DbSession):
    if data.role == UserRole.admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot self-register as admin")
    try:
        user = await auth_service.register_user(db, data.email, data.password, data.role, data.name)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return user


@router.post("/login", response_model=TokenResponse)
@limiter.limit("10/minute")
async def login(request: Request, response: Response, data: LoginRequest, db: DbSession):
    user = await auth_service.authenticate_user(db, data.email, data.password)
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    mfa_pending = user.role == UserRole.admin and user.mfa_enabled
    access, refresh = auth_service.build_tokens(user, mfa_pending=mfa_pending)
    csrf = csrf_cookie_value()
    _set_auth_cookies(response, access, refresh, csrf)
    return TokenResponse(access_token=access, csrf_token=csrf, mfa_required=mfa_pending)


@router.post("/mfa/verify", response_model=TokenResponse)
@limiter.limit("10/minute")
async def mfa_verify(request: Request, response: Response, data: MfaVerifyRequest, db: DbSession):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    payload = verify_token(token, "access")
    if not payload or not payload.get("mfa_pending"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="MFA not required")

    result = await db.execute(select(User).where(User.id == int(payload["sub"])))
    user = result.scalar_one_or_none()
    if not user or not auth_service.verify_mfa_code(user, data.code):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid MFA code")

    access, refresh = auth_service.build_tokens(user, mfa_pending=False)
    csrf = csrf_cookie_value()
    _set_auth_cookies(response, access, refresh, csrf)
    return TokenResponse(access_token=access, csrf_token=csrf)


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(request: Request, response: Response, db: DbSession):
    token = request.cookies.get("refresh_token")
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No refresh token")
    payload = verify_token(token, "refresh")
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    result = await db.execute(select(User).where(User.id == int(payload["sub"])))
    user = result.scalar_one_or_none()
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User inactive")

    access, refresh = auth_service.build_tokens(user)
    csrf = request.cookies.get("csrf_token") or csrf_cookie_value()
    _set_auth_cookies(response, access, refresh, csrf)
    return TokenResponse(access_token=access, csrf_token=csrf)


@router.post("/logout", response_model=MessageResponse)
async def logout(response: Response):
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")
    response.delete_cookie("csrf_token")
    return MessageResponse(message="Logged out")

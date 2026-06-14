from functools import wraps

from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit_log import AuditLog


async def log_audit(
    db: AsyncSession,
    actor_id: int | None,
    action: str,
    resource: str,
    metadata: dict | None = None,
    ip: str | None = None,
) -> None:
    entry = AuditLog(
        actor_id=actor_id,
        action=action,
        resource=resource,
        metadata_=metadata or {},
        ip=ip,
    )
    db.add(entry)


def audit_action(action: str, resource_fn):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            request: Request | None = kwargs.get("request")
            db: AsyncSession | None = kwargs.get("db")
            current_user = kwargs.get("current_user")
            result = await func(*args, **kwargs)
            if db and current_user:
                await log_audit(
                    db,
                    current_user.id,
                    action,
                    resource_fn(kwargs, result),
                    ip=request.client.host if request and request.client else None,
                )
            return result

        return wrapper

    return decorator

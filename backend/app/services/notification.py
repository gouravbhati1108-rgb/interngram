from sqlalchemy.ext.asyncio import AsyncSession

from app.models.notification import Notification


async def create_notification(
    db: AsyncSession,
    user_id: int,
    notif_type: str,
    payload: dict,
) -> Notification:
    notif = Notification(user_id=user_id, type=notif_type, payload=payload)
    db.add(notif)
    await db.flush()
    return notif


async def notify_application_status(db: AsyncSession, user_id: int, application_id: int, status: str) -> None:
    await create_notification(
        db,
        user_id,
        "application_status",
        {"application_id": application_id, "status": status},
    )


async def notify_verification_decision(
    db: AsyncSession, user_id: int, doc_id: int, status: str
) -> None:
    await create_notification(
        db,
        user_id,
        "verification_decision",
        {"document_id": doc_id, "status": status},
    )


async def notify_review_moderation(db: AsyncSession, user_id: int, review_id: int, status: str) -> None:
    await create_notification(
        db,
        user_id,
        "review_moderation",
        {"review_id": review_id, "status": status},
    )

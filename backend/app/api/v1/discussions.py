from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select

from app.core.deps import CurrentUser, DbSession, require_csrf
from app.core.sanitize import sanitize_html
from app.models import Comment, Company, DiscussionPost
from app.models.report import Report, ReportStatus, ReportTarget
from app.schemas.discussion import CommentCreate, CommentResponse, PostCreate, PostResponse, ReportCreate

router = APIRouter(prefix="/discussions", tags=["discussions"])


@router.get("/company/{company_slug}", response_model=list[PostResponse])
async def list_posts(company_slug: str, db: DbSession):
    company = await db.execute(select(Company).where(Company.slug == company_slug))
    company = company.scalar_one_or_none()
    if not company:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found")
    result = await db.execute(
        select(DiscussionPost)
        .where(DiscussionPost.company_id == company.id)
        .order_by(DiscussionPost.is_pinned.desc(), DiscussionPost.created_at.desc())
    )
    return list(result.scalars().all())


@router.post("/company/{company_slug}", response_model=PostResponse, dependencies=[Depends(require_csrf)])
async def create_post(company_slug: str, data: PostCreate, current_user: CurrentUser, db: DbSession):
    company = await db.execute(select(Company).where(Company.slug == company_slug))
    company = company.scalar_one_or_none()
    if not company:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found")
    post = DiscussionPost(
        company_id=company.id,
        author_id=current_user.id,
        title=data.title,
        body=sanitize_html(data.body),
    )
    db.add(post)
    await db.flush()
    return post


@router.get("/posts/{post_id}/comments", response_model=list[CommentResponse])
async def list_comments(post_id: int, db: DbSession):
    result = await db.execute(select(Comment).where(Comment.post_id == post_id).order_by(Comment.created_at))
    return list(result.scalars().all())


@router.post("/posts/{post_id}/comments", response_model=CommentResponse, dependencies=[Depends(require_csrf)])
async def create_comment(post_id: int, data: CommentCreate, current_user: CurrentUser, db: DbSession):
    post = await db.get(DiscussionPost, post_id)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    comment = Comment(
        post_id=post_id,
        author_id=current_user.id,
        body=sanitize_html(data.body),
        parent_id=data.parent_id,
    )
    db.add(comment)
    await db.flush()
    return comment


@router.post("/report", dependencies=[Depends(require_csrf)])
async def report_content(data: ReportCreate, current_user: CurrentUser, db: DbSession):
    report = Report(
        reporter_id=current_user.id,
        target_type=ReportTarget(data.target_type),
        target_id=data.target_id,
        reason=data.reason,
        status=ReportStatus.pending,
    )
    db.add(report)
    await db.flush()
    return {"id": report.id, "status": report.status.value}

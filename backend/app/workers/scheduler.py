from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from app.core.database import AsyncSessionLocal
from app.services.ranking import recalculate_all_rankings


async def nightly_ranking_job():
    async with AsyncSessionLocal() as db:
        try:
            await recalculate_all_rankings(db)
            await db.commit()
        except Exception:
            await db.rollback()
            raise


def start_scheduler() -> AsyncIOScheduler:
    scheduler = AsyncIOScheduler()
    scheduler.add_job(nightly_ranking_job, CronTrigger(hour=2, minute=0), id="ranking_recalc")
    scheduler.start()
    return scheduler

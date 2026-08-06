from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.scheduler.publisher import process_scheduled_posts

scheduler = AsyncIOScheduler()


def start_scheduler():
    scheduler.add_job(
        process_scheduled_posts,
        "interval",
        seconds=30,
        id="publish_scheduled_posts",
        replace_existing=True
    )
    scheduler.start()


def stop_scheduler():
    if scheduler.running:
        scheduler.shutdown()

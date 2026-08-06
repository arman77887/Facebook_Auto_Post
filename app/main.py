import async_timeout
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.config import settings
from app.database.session import engine, Base
from app.scheduler.manager import start_scheduler, stop_scheduler
from app.routers import auth, webhooks
from app.handlers.bot import build_telegram_application


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    start_scheduler()
    bot_app = build_telegram_application()
    await bot_app.initialize()
    await bot_app.start()
    await bot_app.updater.start_polling()

    yield

    await bot_app.updater.stop()
    await bot_app.stop()
    await bot_app.shutdown()
    stop_scheduler()

app = FastAPI(
    title=settings.APP_NAME,
    lifespan=lifespan
)

app.mount("/static", StaticFiles(directory="app/static"), name="static")

app.include_router(auth.router)
app.include_router(webhooks.router)


@app.get("/")
async def root():
    return {"status": "online", "app": settings.APP_NAME, "version": "1.0.0"}

from datetime import datetime, timezone
import logging
import os
from contextlib import asynccontextmanager

from apscheduler.schedulers.background import BackgroundScheduler
from fastapi import FastAPI

from app.api.routes import router
from app.core.config import settings
from app.workers.usgs_poller import poll_usgs

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
)

logger = logging.getLogger("main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    if os.getenv("TESTING"):
        logger.info("Modo TESTING — USGS poller desactivado")
        yield
        return

    scheduler = BackgroundScheduler()
    scheduler.add_job(
        poll_usgs,
        trigger="interval",
        seconds=settings.usgs_poll_interval,
        id="usgs_poller",
        replace_existing=True,
        max_instances=1,
        next_run_time=datetime.now(timezone.utc),
    )
    scheduler.start()
    logger.info(
        f"USGS poller arrancado — intervalo: {settings.usgs_poll_interval}s "
        f"({settings.usgs_poll_interval // 60} min)"
    )

    try:
        yield
    finally:
        scheduler.shutdown(wait=False)
        logger.info("USGS poller detenido")


app = FastAPI(title=settings.app_name, lifespan=lifespan)
app.include_router(router)


@app.get("/")
def root():
    return {"app": settings.app_name, "status": "running"}


@app.get("/health")
def health():
    return {"status": "ok"}
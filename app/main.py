from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from supabase import AsyncClient
import logging

from app.scheduler.scheduler import ScrapingScheduler

from app.core.config import settings
from app.db.supabase import create_supabase_client
from app.api.routes.news_sources import router as news_sources_router
from app.api.routes.scraped_articles import (
    router as scraped_articles_router,
)
from app.api.routes.scraping import router as scraping_router
from app.core.logger import setup_logging
setup_logging()
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize Supabase client
    app.state.supabase = await create_supabase_client()

    # Initialize and start scraping scheduler
    app.state.scraping_scheduler = ScrapingScheduler(
        supabase=app.state.supabase
    )

    app.state.scraping_scheduler.start()

    logger.info("Application startup completed")

    yield

    # Stop scheduler before closing Supabase
    await app.state.scraping_scheduler.shutdown()

    await app.state.supabase.postgrest.aclose()

    logger.info("Application shutdown completed")



app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan,
)
app.include_router(news_sources_router)
app.include_router(scraped_articles_router)
app.include_router(scraping_router)


def get_supabase(request: Request) -> AsyncClient:
    return request.app.state.supabase


@app.get("/health")
async def health_check():
    return {"status": "ok"}

@app.get("/health/database")
async def database_health(request: Request):
    supabase: AsyncClient = request.app.state.supabase

    result = (
        await supabase
        .table("news_sources")
        .select("id, name, base_url, is_active")
        .limit(5)
        .execute()
    )

    return {
        "status": "connected",
        "sources": result.data,
    }
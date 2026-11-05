from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from supabase import AsyncClient

from app.core.config import settings
from app.db.supabase import create_supabase_client


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Application startup
    app.state.supabase = await create_supabase_client()

    yield

    # Application shutdown
    await app.state.supabase.aclose()


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan,
)


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
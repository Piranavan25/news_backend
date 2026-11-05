from supabase import AsyncClient, acreate_client

from app.core.config import settings


async def create_supabase_client() -> AsyncClient:
    return await acreate_client(
        settings.SUPABASE_URL,
        settings.SUPABASE_SECRET_KEY,
    )
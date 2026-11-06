from datetime import datetime, timezone
from typing import Any
from uuid import UUID

from supabase import AsyncClient


class NewsSourceRepository:
    def __init__(self, supabase: AsyncClient):
        self.supabase = supabase

    async def get_active_sources(self) -> list[dict[str, Any]]:
        response = (
            await self.supabase
            .table("news_sources")
            .select("*")
            .eq("is_active", True)
            .order("name")
            .execute()
        )
        return response.data or []

    async def get_source_by_id(
        self, source_id: UUID
    ) -> dict[str, Any] | None:
        response = (
            await self.supabase
            .table("news_sources")
            .select("*")
            .eq("id", str(source_id))
            .limit(1)
            .execute()
        )
        return response.data[0] if response.data else None

    async def get_active_sections(
        self, source_id: UUID
    ) -> list[dict[str, Any]]:
        response = (
            await self.supabase
            .table("news_source_sections")
            .select("*")
            .eq("source_id", str(source_id))
            .eq("is_active", True)
            .order("name")
            .execute()
        )
        return response.data or []

    async def update_scrape_status(
        self, source_id: UUID, status: str
    ) -> None:
        await (
            self.supabase
            .table("news_sources")
            .update({
                "last_scraped_at": datetime.now(timezone.utc).isoformat(),
                "last_scrape_status": status,
            })
            .eq("id", str(source_id))
            .execute()
        )
from typing import Any
from uuid import UUID

from supabase import AsyncClient

from app.schemas.scraped_article import ScrapedArticleCreate


class ScrapedArticleRepository:

    def __init__(self, supabase: AsyncClient):
        self.supabase = supabase

    async def create(
        self,
        article: ScrapedArticleCreate,
    ) -> dict[str, Any]:

        article_data = article.model_dump(mode="json")

        response = (
            await self.supabase
            .table("scraped_articles")
            .insert(article_data)
            .execute()
        )

        return response.data[0]

    async def get_by_canonical_url(
        self,
        source_id: UUID,
        canonical_url: str,
    ) -> dict[str, Any] | None:

        response = (
            await self.supabase
            .table("scraped_articles")
            .select("*")
            .eq("source_id", str(source_id))
            .eq("canonical_url", canonical_url)
            .limit(1)
            .execute()
        )

        return response.data[0] if response.data else None

    async def get_pending(
        self,
        limit: int = 50,
    ) -> list[dict[str, Any]]:

        response = (
            await self.supabase
            .table("scraped_articles")
            .select("*")
            .eq("status", "pending")
            .order("scraped_at", desc=True)
            .limit(limit)
            .execute()
        )

        return response.data or []

    async def get_by_id(
        self,
        article_id: UUID,
    ) -> dict[str, Any] | None:

        response = (
            await self.supabase
            .table("scraped_articles")
            .select("*")
            .eq("id", str(article_id))
            .limit(1)
            .execute()
        )

        return response.data[0] if response.data else None

    async def update_status(
        self,
        article_id: UUID,
        status: str,
    ) -> dict[str, Any] | None:

        response = (
            await self.supabase
            .table("scraped_articles")
            .update({"status": status})
            .eq("id", str(article_id))
            .execute()
        )

        return response.data[0] if response.data else None

    async def get_by_status(
        self,
        status: str,
        limit: int = 50,
    ) -> list[dict[str, Any]]:

        response = (
            await self.supabase
            .table("scraped_articles")
            .select("*")
            .eq("status", status)
            .order("scraped_at", desc=True)
            .limit(limit)
            .execute()
        )

        return response.data or []
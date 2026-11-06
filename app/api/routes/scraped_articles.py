from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, Request
from supabase import AsyncClient

from app.repositories.scraped_article_repository import (
    ScrapedArticleRepository,
)
from app.schemas.scraped_article import ScrapedArticleStatusUpdate


router = APIRouter(
    prefix="/api/scraped-articles",
    tags=["Scraped Articles"],
)


def get_repository(request: Request) -> ScrapedArticleRepository:
    supabase: AsyncClient = request.app.state.supabase
    return ScrapedArticleRepository(supabase)


@router.get("/")
async def get_scraped_articles(
    request: Request,
    status: str | None = None,
    limit: int = Query(default=50, ge=1, le=100),
):
    repository = get_repository(request)

    if status:
        articles = await repository.get_by_status(status, limit)
    else:
        articles = await repository.get_by_status("pending", limit)

    return {
        "total": len(articles),
        "articles": articles,
    }


@router.get("/pending")
async def get_pending_articles(
    request: Request,
    limit: int = Query(default=50, ge=1, le=100),
):
    repository = get_repository(request)

    articles = await repository.get_pending(limit)

    return {
        "total": len(articles),
        "articles": articles,
    }


@router.get("/{article_id}")
async def get_scraped_article(
    article_id: UUID,
    request: Request,
):
    repository = get_repository(request)

    article = await repository.get_by_id(article_id)

    if article is None:
        raise HTTPException(
            status_code=404,
            detail="Scraped article not found",
        )

    return article


@router.patch("/{article_id}/status")
async def update_scraped_article_status(
    article_id: UUID,
    payload: ScrapedArticleStatusUpdate,
    request: Request,
):
    repository = get_repository(request)

    article = await repository.update_status(
        article_id,
        payload.status,
    )

    if article is None:
        raise HTTPException(
            status_code=404,
            detail="Scraped article not found",
        )

    return article
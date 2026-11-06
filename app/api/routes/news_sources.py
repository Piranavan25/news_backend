from uuid import UUID

from fastapi import APIRouter, HTTPException, Request
from supabase import AsyncClient

from app.repositories.news_source_repository import NewsSourceRepository


router = APIRouter(
    prefix="/api/sources",
    tags=["News Sources"],
)


def get_repository(request: Request) -> NewsSourceRepository:
    supabase: AsyncClient = request.app.state.supabase
    return NewsSourceRepository(supabase)


@router.get("/")
async def get_active_sources(request: Request):
    repository = get_repository(request)

    sources = await repository.get_active_sources()

    return {
        "total": len(sources),
        "sources": sources,
    }


@router.get("/{source_id}")
async def get_source(source_id: UUID, request: Request):
    repository = get_repository(request)

    source = await repository.get_source_by_id(source_id)

    if source is None:
        raise HTTPException(
            status_code=404,
            detail="News source not found",
        )

    return source


@router.get("/{source_id}/sections")
async def get_source_sections(source_id: UUID, request: Request):
    repository = get_repository(request)

    source = await repository.get_source_by_id(source_id)

    if source is None:
        raise HTTPException(
            status_code=404,
            detail="News source not found",
        )

    sections = await repository.get_active_sections(source_id)

    return {
        "source_id": str(source_id),
        "total": len(sections),
        "sections": sections,
    }
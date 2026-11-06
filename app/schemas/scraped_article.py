from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, HttpUrl


ScrapedArticleStatus = Literal[
    "pending",
    "approved",
    "rejected",
    "duplicate",
    "failed",
]


class ScrapedArticleCreate(BaseModel):
    source_id: UUID
    section_id: UUID | None = None

    original_url: HttpUrl
    canonical_url: HttpUrl

    title: str
    excerpt: str | None = None
    content: str | None = None
    image_url: HttpUrl | None = None

    language: str = "ta"
    category: str
    published_at: datetime | None = None


class ScrapedArticleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    source_id: UUID
    section_id: UUID | None = None

    original_url: str
    canonical_url: str

    title: str
    excerpt: str | None = None
    content: str | None = None
    image_url: str | None = None

    language: str
    category: str
    published_at: datetime | None = None

    status: ScrapedArticleStatus
    article_id: UUID | None = None
    scraped_at: datetime
    created_at: datetime
    updated_at: datetime


class ScrapedArticleStatusUpdate(BaseModel):
    status: Literal["approved", "rejected"]
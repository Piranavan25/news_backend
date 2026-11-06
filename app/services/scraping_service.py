import logging
from typing import Any

from app.core.config import settings
from app.repositories.news_source_repository import NewsSourceRepository
from app.repositories.scraped_article_repository import ScrapedArticleRepository
from app.schemas.scraped_article import ScrapedArticleCreate
from app.scraping.engine import ScrapingEngine
from app.scraping.http_client import ScrapingHTTPClient
from app.scraping.url_normalizer import normalize_url


logger = logging.getLogger(__name__)


class ScrapingService:

    def __init__(
        self,
        source_repository: NewsSourceRepository,
        article_repository: ScrapedArticleRepository,
        http_client: ScrapingHTTPClient,
    ):
        self.source_repository = source_repository
        self.article_repository = article_repository
        self.http_client = http_client

        self.engine = ScrapingEngine(
            http_client=http_client,
            max_concurrent_articles=settings.MAX_CONCURRENT_ARTICLES,
        )

    async def scrape_all_sources(self) -> dict[str, Any]:

        sources = await self.source_repository.get_active_sources()

        results = []

        for source in sources:
            result = await self.scrape_source(source)
            results.append(result)

        return {
            "total_sources": len(sources),
            "results": results,
        }

    async def scrape_source(
        self,
        source: dict[str, Any],
    ) -> dict[str, Any]:

        source_id = source["id"]

        result = {
            "source_id": source_id,
            "source_name": source["name"],
            "sections_processed": 0,
            "articles_found": 0,
            "articles_saved": 0,
            "duplicates_skipped": 0,
            "articles_failed": 0,
            "errors": [],
        }

        try:
            sections = await self.source_repository.get_active_sections(
                source_id
            )

            for section in sections:
                try:
                    articles = await self.engine.scrape_section(
                        listing_url=section["listing_url"],
                        base_url=source["base_url"],
                        selectors=section["selectors"],
                        article_selectors=section.get("article_selectors") or {},

                    )

                    result["sections_processed"] += 1
                    result["articles_found"] += len(articles)

                    for article in articles:
                        try:
                            canonical_url = normalize_url(
                                article["canonical_url"]
                            )


                            existing = (
                                await self.article_repository
                                .get_by_canonical_url(
                                    source_id=source_id,
                                    canonical_url=canonical_url,
                                )
                            )



                            if existing:
                                result["duplicates_skipped"] += 1
                                continue

                            article_data = ScrapedArticleCreate(
                                source_id=source_id,
                                section_id=section["id"],
                                original_url=article["original_url"],
                                canonical_url=canonical_url,
                                title=article["title"],
                                content=article.get("content"),
                                image_url=article.get("image_url"),
                                language=source["language"],
                                category=section["category"],
                                published_at=article.get("published_at"),
                            )

                            await self.article_repository.create(
                                article_data
                            )

                            result["articles_saved"] += 1

                        except Exception as exc:
                            result["articles_failed"] += 1
                            logger.exception(
                                "Failed to save article: %s",
                                article.get("original_url"),
                            )
                            result["errors"].append(str(exc))

                except Exception as exc:
                    logger.exception(
                        "Failed to scrape section: %s",
                        section["listing_url"],
                    )
                    result["errors"].append(str(exc))

            status = (
                "success"
                if not result["errors"]
                else "partial_success"
            )

            await self.source_repository.update_scrape_status(
                source_id,
                status,
            )

        except Exception as exc:
            logger.exception(
                "Failed to scrape source: %s",
                source["name"],
            )

            result["errors"].append(str(exc))

            await self.source_repository.update_scrape_status(
                source_id,
                "failed",
            )

        return result
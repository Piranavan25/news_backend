
import asyncio
import logging
from typing import Any

from app.scraping.http_client import ScrapingHTTPClient
from app.scraping.listing_extractor import ListingExtractor
from app.scraping.article_extractor import ArticleExtractor

logger = logging.getLogger(__name__)


class ScrapingEngine:

    def __init__(
        self,
        http_client: ScrapingHTTPClient,
        max_concurrent_articles: int = 5,
        max_articles_per_section: int = 20,
    ):
        self.http_client = http_client
        self.listing_extractor = ListingExtractor()
        self.article_extractor = ArticleExtractor()
        self.semaphore = asyncio.Semaphore(max_concurrent_articles)
        self.max_articles_per_section = max_articles_per_section

    async def scrape_section(
        self,
        listing_url: str,
        base_url: str,
        selectors: dict[str, Any],
        article_selectors: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:

        logger.info("Scraping listing page: %s", listing_url)

        html = await self.http_client.fetch_html(listing_url)

        articles = self.listing_extractor.extract_articles(
            html=html,
            base_url=base_url,
            selectors=selectors,
        )

        total_found = len(articles)

        articles = articles[:self.max_articles_per_section]

        logger.info(
            "Found %s articles; processing %s",
            total_found,
            len(articles),
        )

        async def process_article(
            article: dict[str, Any],
        ) -> dict[str, Any] | None:

            async with self.semaphore:
                try:
                    article_html = await self.http_client.fetch_html(
                        article["original_url"]
                    )

                    details = self.article_extractor.extract_article(
                        html=article_html,
                        selectors=article_selectors,
                    )

                    return {
                        **article,
                        **details,
                        "title": details.get("title") or article.get("title"),

                    }

                except Exception:
                    logger.exception(
                        "Failed to extract article: %s",
                        article["original_url"],
                    )
                    return None

        results = await asyncio.gather(
            *(process_article(article) for article in articles)
        )

        return [
            article
            for article in results
            if article is not None
        ]

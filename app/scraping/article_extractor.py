
from typing import Any
import re

import trafilatura

from app.scraping.extractors.generic_extractor import (
    GenericHTMLExtractor,
)


class ArticleExtractor:

    def extract_article(
        self,
        html: str,
        selectors: dict[str, Any] | None = None,
    ) -> dict[str, Any]:

        selectors = selectors or {}
        extractor = GenericHTMLExtractor(html)

        # 1. Extract title
        title = None

        title_selector = selectors.get("title")

        if title_selector:
            title_element = extractor.select_one(title_selector)
            title = extractor.get_text(title_element)

        if not title:
            title_element = extractor.select_one(
                'meta[property="og:title"]'
            )
            title = extractor.get_attribute(
                title_element,
                "content",
            )

        if not title:
            title_element = extractor.select_one("title")
            title = extractor.get_text(title_element)

        # 2. Extract publication date
        published_at = None

        date_selector = selectors.get("published_at")

        if date_selector:
            date_element = extractor.select_one(date_selector)

            published_at = (
                extractor.get_attribute(date_element, "datetime")
                or extractor.get_attribute(date_element, "content")
                or extractor.get_text(date_element)
            )

        if not published_at:
            date_element = extractor.select_one(
                'meta[property="article:published_time"]'
            )
            published_at = extractor.get_attribute(
                date_element,
                "content",
            )

        # 3. Extract author
        author = None

        author_selector = selectors.get("author")

        if author_selector:
            author_element = extractor.select_one(author_selector)
            author = extractor.get_text(author_element)

        if not author:
            author_element = extractor.select_one(
                'meta[name="author"]'
            )
            author = extractor.get_attribute(
                author_element,
                "content",
            )

        # 4. Extract article content using Trafilatura
        content = trafilatura.extract(
            html,
            include_comments=False,
            include_tables=True,
            favor_precision=True,
        )

        # 5. Fallback to configured content selector
        if not content:
            content_selector = selectors.get("content")

            if content_selector:
                content_element = extractor.select_one(
                    content_selector
                )

                content = extractor.get_text(
                    content_element,
                    separator="\n",
                )

        if content:
            content = re.sub(r"[ \t]+", " ", content)
            content = re.sub(r"(?<=[a-zA-Z])(?=[A-Z])", " ", content)
            content = re.sub(r"\n{3,}", "\n\n", content)

        # 6. Normalize extracted values
        return {
            "title": title.strip() if title else None,
            "content": content.strip() if content else None,
            "published_at": published_at.strip() if published_at else None,
            "author": author.strip() if author else None,
        }

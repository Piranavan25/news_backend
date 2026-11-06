from typing import Any
from urllib.parse import urljoin

from app.scraping.extractors.generic_extractor import (
    GenericHTMLExtractor,
)
from app.scraping.url_normalizer import normalize_url


class ListingExtractor:

    def extract_articles(
        self,
        html: str,
        base_url: str,
        selectors: dict[str, str],
    ) -> list[dict[str, Any]]:

        extractor = GenericHTMLExtractor(html)

        articles = []

        section_selector = selectors.get("section")
        card_selector = selectors.get("article_card")

        if not card_selector:
            raise ValueError("Missing article_card selector")

        # Restrict extraction to the configured section, if provided.
        section = (
            extractor.select_one(section_selector)
            if section_selector
            else None
        )

        if section_selector and section is None:
            raise ValueError(
                f"Section selector not found: {section_selector}"
            )

        container = section if section is not None else extractor.soup

        cards = extractor.select_all(card_selector, container)

        for card in cards:

            title_selector = selectors.get("title_link") or selectors.get("title")
            link_selector = selectors.get("link") or selectors.get("title_link")
            image_selector = selectors.get("image")

            title_element = (
                extractor.select_one(title_selector, card)
                if title_selector
                else None
            )

            link_element = (
                extractor.select_one(link_selector, card)
                if link_selector
                else title_element
            )

            image_element = (
                extractor.select_one(image_selector, card)
                if image_selector
                else None
            )

            title = extractor.get_text(title_element)

            href = extractor.get_attribute(link_element, "href")

            if not title or not href:
                continue

            original_url = urljoin(base_url, href)

            try:
                canonical_url = normalize_url(original_url)
            except ValueError:
                continue

            image_url = (
                extractor.get_attribute(image_element, "data-src")
                or extractor.get_attribute(image_element, "data-original")
                or extractor.get_attribute(image_element, "src")
)

            if image_url:
                image_url = urljoin(base_url, image_url)

            articles.append({
                "title": title,
                "original_url": original_url,
                "canonical_url": canonical_url,
                "image_url": image_url,
            })

        return articles
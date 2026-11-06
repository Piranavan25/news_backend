from typing import Any

from bs4 import BeautifulSoup, Tag


class GenericHTMLExtractor:

    def __init__(self, html: str):
        self.soup = BeautifulSoup(html, "html.parser")

    def select_one(
        self,
        selector: str,
        parent: Tag | BeautifulSoup | None = None,
    ) -> Tag | None:
        """
        Find the first element matching a CSS selector.
        """
        container = parent or self.soup
        return container.select_one(selector)

    def select_all(
        self,
        selector: str,
        parent: Tag | BeautifulSoup | None = None,
    ) -> list[Tag]:
        """
        Find all elements matching a CSS selector.
        """
        container = parent or self.soup
        return container.select(selector)

    def get_text(
        self,
        element: Tag | None,
        separator: str = " ",
    ) -> str | None:
        """
        Extract clean text from an HTML element.
        """
        if element is None:
            return None

        text = element.get_text(
            separator=separator,
            strip=True,
        )

        return text or None

    def get_attribute(
        self,
        element: Tag | None,
        attribute: str,
    ) -> str | None:
        """
        Extract an HTML attribute such as href or src.
        """
        if element is None:
            return None

        value = element.get(attribute)

        if isinstance(value, list):
            value = " ".join(str(item) for item in value)

        if value is None:
            return None

        value = str(value).strip()

        return value or None

    def extract(
        self,
        html: str,
        selectors: dict[str, str],
    ) -> dict[str, Any]:
        """
        Extract multiple fields from HTML using CSS selectors.
        """
        extractor = GenericHTMLExtractor(html)

        result = {}

        for field, selector in selectors.items():
            element = extractor.select_one(selector)
            result[field] = extractor.get_text(element)

        return result
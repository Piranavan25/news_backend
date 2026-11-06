import httpx

from app.core.config import settings


class ScrapingHTTPClient:

    def __init__(self):
        self.client = httpx.AsyncClient(
            timeout=settings.HTTP_TIMEOUT,
            limits=httpx.Limits(
                max_connections=settings.HTTP_MAX_CONNECTIONS,
                max_keepalive_connections=settings.HTTP_MAX_KEEPALIVE_CONNECTIONS,
            ),
            follow_redirects=True,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/120.0.0.0 Safari/537.36"
                )
            },
        )

    async def fetch_html(self, url: str) -> str:
        response = await self.client.get(url)
        response.raise_for_status()

        return response.text

    async def close(self):
        await self.client.aclose()
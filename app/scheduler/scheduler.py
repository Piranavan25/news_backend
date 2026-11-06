
import asyncio
import logging
from datetime import datetime

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

from app.core.config import settings
from app.repositories.news_source_repository import NewsSourceRepository
from app.repositories.scraped_article_repository import (
    ScrapedArticleRepository,
)
from app.scraping.http_client import ScrapingHTTPClient
from app.services.scraping_service import ScrapingService

logger = logging.getLogger(__name__)


class ScrapingScheduler:

    def __init__(self, supabase):
        self.supabase = supabase

        self.scheduler = AsyncIOScheduler(
            timezone=settings.SCRAPING_TIMEZONE
        )

        self.job_lock = asyncio.Lock()
        self.is_shutting_down = False

    async def run_scraping_job(self):
        await self._execute_scraping("Scheduled scraping")

    def start(self):
        if self.scheduler.running:
            logger.warning("Scraping scheduler is already running")
            return

        mode = settings.SCRAPING_SCHEDULE_MODE.lower()

        if mode not in {"interval", "daily", "both"}:
            raise ValueError(
                f"Invalid scraping schedule mode: {mode}"
            )

        # Interval-based schedule.
        if mode in {"interval", "both"}:
            if settings.SCRAPING_INTERVAL_MINUTES <= 0:
                raise ValueError(
                    "SCRAPING_INTERVAL_MINUTES must be greater than zero"
                )

            self.scheduler.add_job(
                self.run_scraping_job,
                trigger=IntervalTrigger(
                    minutes=settings.SCRAPING_INTERVAL_MINUTES,
                    timezone=settings.SCRAPING_TIMEZONE,
                ),
                id="news_scraping_interval",
                name="Interval-based news scraping",
                max_instances=1,
                coalesce=True,
                replace_existing=True,
            )

            logger.info(
                "Interval scraping configured: every %s minutes",
                settings.SCRAPING_INTERVAL_MINUTES,
            )

        # Specific daily schedules.
        if mode in {"daily", "both"}:
            for time_value in settings.SCRAPING_DAILY_TIMES:
                try:
                    scheduled_time = datetime.strptime(
                        time_value, "%H:%M"
                    )
                except ValueError as exc:
                    raise ValueError(
                        f"Invalid daily scraping time: {time_value}. "
                        "Expected HH:MM format."
                    ) from exc

                job_id = (
                    f"news_scraping_daily_"
                    f"{scheduled_time.hour:02d}_"
                    f"{scheduled_time.minute:02d}"
                )

                self.scheduler.add_job(
                    self.run_scraping_job,
                    trigger=CronTrigger(
                        hour=scheduled_time.hour,
                        minute=scheduled_time.minute,
                        timezone=settings.SCRAPING_TIMEZONE,
                    ),
                    id=job_id,
                    name=f"Daily news scraping at {time_value}",
                    max_instances=1,
                    coalesce=True,
                    replace_existing=True,
                )

                logger.info(
                    "Daily scraping configured at %s",
                    time_value,
                )

        self.scheduler.start()

        logger.info(
            "Scraping scheduler started in '%s' mode",
            mode,
        )


    async def shutdown(self):
        self.is_shutting_down = True
        if self.scheduler.running:
            self.scheduler.pause()
            self.scheduler.shutdown(wait=False)
            logger.info("Scraping scheduler stopped")

        logger.info("Waiting for active scraping job to finish...")

        async with self.job_lock:
            pass

        logger.info("Active scraping job finished")

    async def run_manual_scraping(self):
        if self.is_shutting_down:
            raise RuntimeError("Application is shutting down.")

        if self.job_lock.locked():
            raise RuntimeError("A scraping job is already running.")

        return await self._execute_scraping("Manual scraping")


    async def _execute_scraping(self, job_name: str):
        if self.is_shutting_down:
            logger.warning(
                "Cannot start %s: scheduler is shutting down.",
                job_name,
            )
            return None

        if self.job_lock.locked():
            logger.warning(
                "Cannot start %s: another scraping job is running.",
                job_name,
            )
            return None

        async with self.job_lock:
            if self.is_shutting_down:
                logger.warning(
                    "Cannot start %s: scheduler is shutting down.",
                    job_name,
                )
                return None

            http_client = ScrapingHTTPClient()

            try:
                logger.info("%s started", job_name)

                source_repository = NewsSourceRepository(self.supabase)
                article_repository = ScrapedArticleRepository(self.supabase)

                service = ScrapingService(
                    source_repository=source_repository,
                    article_repository=article_repository,
                    http_client=http_client,
                )

                result = await service.scrape_all_sources()

                logger.info("%s completed: %s", job_name, result)

                return result

            except Exception:
                logger.exception("%s failed", job_name)
                raise

            finally:
                await http_client.close()
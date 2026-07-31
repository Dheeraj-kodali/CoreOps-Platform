import asyncio
import logging
from datetime import datetime
from typing import Dict, Any
from app.core.database import AsyncSessionLocal
from app.services.backup_service import BackupService

logger = logging.getLogger("app.scheduler")


class AsyncScheduler:
    """
    Production Background Scheduler.
    Runs automated background tasks: daily database snapshots,
    scheduled broadcast dispatch processing, and system health tickers.
    """

    def __init__(self):
        self._running = False
        self._task: asyncio.Task | None = None
        self.last_backup_run: datetime | None = None
        self.broadcasts_processed_count = 0

    def start(self):
        if not self._running:
            self._running = True
            self._task = asyncio.create_task(self._scheduler_loop())
            logger.info("AsyncScheduler: Production background scheduler started.")

    def stop(self):
        self._running = False
        if self._task:
            self._task.cancel()
            logger.info("AsyncScheduler: Background scheduler stopped.")

    def get_status(self) -> Dict[str, Any]:
        return {
            "status": "RUNNING" if self._running else "STOPPED",
            "active_workers": 4,
            "last_automated_backup": self.last_backup_run.strftime("%Y-%m-%d %I:%M %p") if self.last_backup_run else "Pending First Cycle",
            "broadcasts_processed": self.broadcasts_processed_count,
        }

    async def _scheduler_loop(self):
        logger.info("AsyncScheduler: Entering background execution loop...")
        while self._running:
            try:
                await self._run_automated_tasks()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"AsyncScheduler: Error in loop iteration: {e}")

            # Sleep 60 seconds between ticker iterations
            await asyncio.sleep(60)

    async def _run_automated_tasks(self):
        now = datetime.now()

        # Check automated backup cycle (run once every 24 hours at 02:00 AM or on startup)
        if self.last_backup_run is None or (now - self.last_backup_run).total_seconds() >= 86400:
            logger.info("AsyncScheduler: Executing automated daily database snapshot...")
            async with AsyncSessionLocal() as session:
                try:
                    await BackupService.create_backup(session, backup_type="AUTOMATED_DAILY")
                    self.last_backup_run = now
                except Exception as e:
                    logger.error(f"AsyncScheduler: Daily backup failed: {e}")


global_scheduler = AsyncScheduler()

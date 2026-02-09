"""Task scheduler for periodic monitoring."""
import logging
import asyncio
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

from config.settings import settings
from src.scheduler.monitor import Monitor

logger = logging.getLogger(__name__)


class TaskScheduler:
    """Task scheduler for monitoring TikTok creators."""
    
    def __init__(self, monitor: Monitor):
        """Initialize scheduler."""
        self.monitor = monitor
        self.scheduler = BackgroundScheduler()
    
    def _run_monitoring(self):
        """Wrapper to run async monitoring in sync context."""
        try:
            asyncio.run(self.monitor.check_all_creators())
        except Exception as e:
            logger.error(f"Error in monitoring cycle: {e}")
    
    def start(self):
        """Start the scheduler."""
        # Add monitoring job
        self.scheduler.add_job(
            func=self._run_monitoring,
            trigger=IntervalTrigger(minutes=settings.MONITOR_INTERVAL_MINUTES),
            id='monitor_creators',
            name='Monitor TikTok creators for new posts',
            replace_existing=True
        )
        
        logger.info(
            f"Scheduler started. Monitoring every {settings.MONITOR_INTERVAL_MINUTES} minutes."
        )
        
        # Run first check immediately in background
        import threading
        threading.Thread(target=self._run_monitoring, daemon=True).start()
        
        # Start scheduler (non-blocking)
        self.scheduler.start()
    
    def stop(self):
        """Stop the scheduler."""
        self.scheduler.shutdown()
        logger.info("Scheduler stopped")

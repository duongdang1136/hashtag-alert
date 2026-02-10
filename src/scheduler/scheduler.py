"""Task scheduling using asyncio instead of APScheduler."""
import logging
import asyncio
from typing import Optional

from config.settings import settings

logger = logging.getLogger(__name__)


class TaskScheduler:
    """Scheduler for periodic monitoring tasks using asyncio."""
    
    def __init__(self, monitor):
        """Initialize scheduler with monitor instance."""
        self.monitor = monitor
        self.task: Optional[asyncio.Task] = None
        self.running = False
        
    async def _monitoring_loop(self):
        """Background monitoring loop that runs periodically."""
        logger.info(f"Monitoring task started (interval: {settings.MONITOR_INTERVAL_MINUTES} minutes)")
        
        while self.running:
            try:
                # Run monitoring check
                await self.monitor.check_all_creators()
                
                # Wait for next interval
                await asyncio.sleep(settings.MONITOR_INTERVAL_MINUTES * 60)
                
            except asyncio.CancelledError:
                logger.info("Monitoring task cancelled")
                break
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}", exc_info=True)
                # Wait a bit before retrying on error
                await asyncio.sleep(60)
    
    def start(self):
        """Start the monitoring task."""
        if self.running:
            logger.warning("Scheduler already running")
            return
            
        self.running = True
        # Create asyncio task (non-blocking)
        self.task = asyncio.create_task(self._monitoring_loop())
        logger.info("Scheduler started successfully")
    
    async def stop(self):
        """Stop the monitoring task."""
        if not self.running:
            return
            
        logger.info("Stopping scheduler...")
        self.running = False
        
        if self.task:
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                pass
        
        logger.info("Scheduler stopped")

"""TikTok Hashtag Alert Bot - Main application."""
import logging
from logging.handlers import RotatingFileHandler
import asyncio
import signal
import sys

from config.settings import settings
from src.database.supabase_client import SupabaseClient
from src.tiktok.scraper import TikTokScraper
from src.bot.telegram_bot import TelegramBot
from src.scheduler.monitor import Monitor
from src.scheduler.scheduler import TaskScheduler

# Setup logging with rotation
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=getattr(logging, settings.LOG_LEVEL),
    handlers=[
        RotatingFileHandler(
            'bot.log',
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5  # Keep 5 old logs
        ),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


class Application:
    """Main application orchestrator."""
    
    def __init__(self):
        """Initialize application."""
        self.db_client = None
        self.tiktok_scraper = None
        self.telegram_bot = None
        self.monitor = None
        self.scheduler = None
        self.running = False
    
    def initialize(self):
        """Initialize all components."""
        try:
            logger.info("Initializing TikTok Hashtag Alert Bot...")
            
            # Validate settings
            settings.validate()
            logger.info("Configuration validated successfully")
            
            # Initialize database client
            self.db_client = SupabaseClient()
            
            # Initialize TikTok scraper
            self.tiktok_scraper = TikTokScraper()
            
            # Initialize Telegram bot
            self.telegram_bot = TelegramBot(self.db_client)
            self.telegram_bot.setup()
            
            # Initialize monitor
            self.monitor = Monitor(
                db_client=self.db_client,
                tiktok_scraper=self.tiktok_scraper,
                telegram_bot=self.telegram_bot
            )
            
            # Initialize scheduler
            self.scheduler = TaskScheduler(self.monitor)
            
            logger.info("All components initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize application: {e}")
            sys.exit(1)
    
    async def start(self):
        """Start the application (async)."""
        self.running = True
        logger.info("TikTok Hashtag Alert Bot is running!")
        
        # Start scheduler task (non-blocking)
        self.scheduler.start()
        
        # Initialize and run Telegram bot
        logger.info("Starting Telegram bot polling...")
        await self.telegram_bot.application.initialize()
        await self.telegram_bot.application.start()
        await self.telegram_bot.application.updater.start_polling()
        
        # Keep running until stopped
        try:
            await asyncio.Event().wait()  # Wait forever
        except asyncio.CancelledError:
            pass
    
    async def stop(self):
        """Stop the application."""
        if not self.running:
            return
        
        logger.info("Stopping application...")
        
        # Stop scheduler
        if self.scheduler:
            await self.scheduler.stop()
        
        # Stop Telegram bot
        if self.telegram_bot and self.telegram_bot.application:
            await self.telegram_bot.application.updater.stop()
            await self.telegram_bot.application.stop()
        
        self.running = False
        logger.info("Application stopped")
    
    async def run(self):
        """Run the application (async)."""
        self.initialize()
        
        try:
            await self.start()
        except KeyboardInterrupt:
            logger.info("Shutdown signal received")
        finally:
            await self.stop()


async def main_async():
    """Async main entry point."""
    app = Application()
    await app.run()


def main():
    """Main entry point."""
    try:
        asyncio.run(main_async())
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()

"""TikTok Hashtag Alert Bot - Main application."""
import logging
from logging.handlers import RotatingFileHandler
import asyncio
import signal
import sys
from threading import Thread

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
        self.bot_thread = None
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
    
    
    def start(self):
        """Start the application."""
        self.initialize()
        
        self.running = True
        logger.info("TikTok Hashtag Alert Bot is running!")
        logger.info("Press Ctrl+C to stop")
        
        # Start scheduler (non-blocking, runs in background)
        self.scheduler.start()
        
        # Run Telegram bot in main thread (blocking)
        # This must run in main thread on Linux
        logger.info("Starting Telegram bot polling...")
        self.telegram_bot.run()
    
    def stop(self):
        """Stop the application."""
        if not self.running:
            return
        
        logger.info("Stopping application...")
        
        # Stop scheduler
        if self.scheduler:
            self.scheduler.stop()
        
        # Stop Telegram bot
        if self.telegram_bot and self.telegram_bot.application:
            asyncio.run(self.telegram_bot.application.stop())
        
        self.running = False
        logger.info("Application stopped")
    
    def run(self):
        """Run the application (blocking)."""
        try:
            # Start application (this will block in telegram bot polling)
            self.start()
        except KeyboardInterrupt:
            logger.info("Shutdown signal received, stopping bot...")
            self.stop()


def main():
    """Main entry point."""
    try:
        app = Application()
        app.run()
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()

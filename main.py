"""TikTok Hashtag Alert Bot - Main application."""
import logging
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

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=getattr(logging, settings.LOG_LEVEL),
    handlers=[
        logging.FileHandler('bot.log'),
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
    
    def start_bot_polling(self):
        """Start Telegram bot in a separate thread."""
        def run_bot():
            try:
                self.telegram_bot.run()
            except Exception as e:
                logger.error(f"Bot polling error: {e}")
        
        self.bot_thread = Thread(target=run_bot, daemon=True)
        self.bot_thread.start()
        logger.info("Telegram bot polling started in background thread")
    
    def start(self):
        """Start the application."""
        self.initialize()
        
        # Start Telegram bot polling
        self.start_bot_polling()
        
        self.running = True
        logger.info("TikTok Hashtag Alert Bot is running!")
        logger.info("Press Ctrl+C to stop")
        
        # Start scheduler (this is blocking and will run until interrupted)
        self.scheduler.start()
    
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
        # Start application
        self.start()
        
        # Keep main thread alive and handle shutdown
        try:
            logger.info("Bot is running. Press Ctrl+C to stop.")
            # Use simple sleep loop instead of asyncio to avoid event loop conflicts
            import time
            while self.running:
                time.sleep(0.5)
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

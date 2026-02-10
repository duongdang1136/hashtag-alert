"""Application settings loaded from environment variables."""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Settings:
    """Application configuration settings."""
    
    # Telegram Bot
    TELEGRAM_BOT_TOKEN: str = os.getenv('TELEGRAM_BOT_TOKEN', '')
    
    # Supabase
    SUPABASE_URL: str = os.getenv('SUPABASE_URL', '')
    SUPABASE_KEY: str = os.getenv('SUPABASE_KEY', '')
    
    # Monitoring
    MONITOR_INTERVAL_MINUTES: int = int(os.getenv('MONITOR_INTERVAL_MINUTES', '10'))
    MAX_POSTS_PER_CHECK: int = int(os.getenv('MAX_POSTS_PER_CHECK', '5'))
    
    # Alert settings
    ALERT_ONLY_RECENT_POSTS: bool = os.getenv('ALERT_ONLY_RECENT_POSTS', 'true').lower() == 'true'
    
    # Logging
    LOG_LEVEL: str = os.getenv('LOG_LEVEL', 'INFO')
    
    # TikTok Scraper
    TIKTOK_REQUEST_DELAY: int = int(os.getenv('TIKTOK_REQUEST_DELAY', '2'))
    TIKTOK_MAX_RETRIES: int = int(os.getenv('TIKTOK_MAX_RETRIES', '3'))
    
    def validate(self) -> bool:
        """Validate required settings are present."""
        required = [
            ('TELEGRAM_BOT_TOKEN', self.TELEGRAM_BOT_TOKEN),
            ('SUPABASE_URL', self.SUPABASE_URL),
            ('SUPABASE_KEY', self.SUPABASE_KEY),
        ]
        
        missing = [name for name, value in required if not value]
        
        if missing:
            raise ValueError(f"Missing required environment variables: {', '.join(missing)}")
        
        return True
    
    def __repr__(self) -> str:
        """String representation (hide sensitive data)."""
        return (
            f"Settings(\n"
            f"  TELEGRAM_BOT_TOKEN={'*' * 10 if self.TELEGRAM_BOT_TOKEN else 'NOT_SET'},\n"
            f"  SUPABASE_URL={self.SUPABASE_URL[:30]}... if self.SUPABASE_URL else 'NOT_SET',\n"
            f"  SUPABASE_KEY={'*' * 10 if self.SUPABASE_KEY else 'NOT_SET'},\n"
            f"  MONITOR_INTERVAL_MINUTES={self.MONITOR_INTERVAL_MINUTES},\n"
            f"  MAX_POSTS_PER_CHECK={self.MAX_POSTS_PER_CHECK},\n"
            f"  LOG_LEVEL={self.LOG_LEVEL}\n"
            f")"
        )


# Global settings instance
settings = Settings()

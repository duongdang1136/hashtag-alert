"""Telegram bot main module."""
import logging
from typing import Dict, Any, List
from telegram import Bot
from telegram.ext import Application, CommandHandler

from config.settings import settings
from src.database.supabase_client import SupabaseClient
from src.bot.handlers import BotHandlers

logger = logging.getLogger(__name__)


class TelegramBot:
    """Telegram bot for sending alerts."""
    
    def __init__(self, db_client: SupabaseClient):
        """Initialize Telegram bot."""
        self.db = db_client
        self.handlers = BotHandlers(db_client)
        self.application = None
        self.bot = None
    
    def setup(self) -> Application:
        """Setup the Telegram bot application."""
        # Create application
        self.application = Application.builder().token(settings.TELEGRAM_BOT_TOKEN).build()
        self.bot = self.application.bot
        
        # Add command handlers
        self.application.add_handler(CommandHandler("start", self.handlers.start_command))
        self.application.add_handler(CommandHandler("help", self.handlers.help_command))
        self.application.add_handler(CommandHandler("add", self.handlers.add_command))
        self.application.add_handler(CommandHandler("remove", self.handlers.remove_command))
        self.application.add_handler(CommandHandler("list", self.handlers.list_command))
        
        # Add error handler
        self.application.add_error_handler(self.handlers.error_handler)
        
        logger.info("Telegram bot setup complete")
        return self.application
    
    async def send_alert(self, telegram_user_id: int, post: Dict[str, Any]):
        """
        Send a new post alert to a Telegram user.
        
        Args:
            telegram_user_id: Telegram user ID to send to
            post: Post information dictionary
        """
        try:
            # Format hashtags
            hashtags_text = " ".join([f"#{tag}" for tag in post.get('hashtags', [])])
            
            # Create message
            message = (
                f"🔔 *Bài viết mới từ @{post.get('author', 'Unknown')}*\n\n"
                f"📝 {post.get('description', 'Không có mô tả')[:200]}...\n\n"
            )
            
            if hashtags_text:
                message += f"🏷️ *Hashtags:* {hashtags_text}\n\n"
            
            message += f"🔗 [Xem bài viết]({post.get('url', '')})"
            
            # Send message
            await self.bot.send_message(
                chat_id=telegram_user_id,
                text=message,
                parse_mode='Markdown',
                disable_web_page_preview=True
            )
            
            logger.info(f"Sent alert to user {telegram_user_id} for post {post.get('id')}")
            
        except Exception as e:
            logger.error(f"Error sending alert to user {telegram_user_id}: {e}")
    
    async def send_alerts_to_all_users(self, post: Dict[str, Any], creator_username: str):
        """
        Send alerts to all users tracking this creator.
        
        Args:
            post: Post information dictionary
            creator_username: TikTok username
        """
        try:
            # Get creator info
            creator = self.db.get_tracked_creator_by_username(creator_username)
            if not creator:
                logger.warning(f"Creator @{creator_username} not found in database")
                return
            
            # For now, we send to the user who added this creator
            # In future, you can extend this to support multiple users per creator
            telegram_user_id = creator.get('added_by_telegram_user')
            
            if telegram_user_id:
                await self.send_alert(telegram_user_id, post)
            
        except Exception as e:
            logger.error(f"Error sending alerts for creator @{creator_username}: {e}")
    
    def run(self):
        """Run the bot (blocking)."""
        logger.info("Starting Telegram bot polling...")
        self.application.run_polling(allowed_updates=['message'])

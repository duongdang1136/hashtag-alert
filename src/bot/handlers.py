"""Telegram bot command handlers."""
import logging
from typing import Optional
from telegram import Update
from telegram.ext import ContextTypes

from src.database.supabase_client import SupabaseClient

logger = logging.getLogger(__name__)


class BotHandlers:
    """Telegram bot command handlers."""
    
    def __init__(self, db_client: SupabaseClient):
        """Initialize handlers with database client."""
        self.db = db_client
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command."""
        user = update.effective_user
        
        # Register user in database
        self.db.add_or_update_bot_user(
            telegram_user_id=user.id,
            username=user.username,
            first_name=user.first_name
        )
        
        welcome_message = (
            f"Chào {user.first_name}! 👋\n\n"
            "🎯 TikTok Hashtag Alert Bot\n\n"
            "Bot này sẽ giúp bạn theo dõi các TikToker và nhận thông báo "
            "khi họ đăng bài mới kèm hashtag.\n\n"
            "📌 Các lệnh có thể dùng:\n"
            "/add <username> - Thêm TikToker vào danh sách theo dõi\n"
            "/remove <username> - Xóa TikToker khỏi danh sách\n"
            "/list - Xem danh sách TikToker đang theo dõi\n"
            "/help - Xem hướng dẫn\n\n"
            "Ví dụ: /add khaby.lame"
        )
        
        await update.message.reply_text(welcome_message)
        logger.info(f"User {user.id} started the bot")
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command."""
        help_message = (
            "📖 Hướng dẫn sử dụng:\n\n"
            "1️⃣ Thêm TikToker để theo dõi:\n"
            "/add <username>\n"
            "Ví dụ: /add khaby.lame\n\n"
            "2️⃣ Xóa TikToker:\n"
            "/remove <username>\n"
            "Ví dụ: /remove khaby.lame\n\n"
            "3️⃣ Xem danh sách:\n"
            "/list\n\n"
            "⚡ Bot sẽ tự động kiểm tra bài viết mới mỗi 10 phút và "
            "gửi thông báo kèm hashtag cho bạn!"
        )
        
        await update.message.reply_text(help_message)
    
    async def add_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /add command to add a TikTok creator."""
        user = update.effective_user
        
        if not context.args or len(context.args) < 1:
            await update.message.reply_text(
                "❌ Vui lòng cung cấp username TikTok!\n"
                "Ví dụ: /add khaby.lame"
            )
            return
        
        tiktok_username = context.args[0].lstrip('@').lower()
        
        # Check if already tracking
        existing = self.db.get_tracked_creator_by_username(tiktok_username)
        
        if existing and existing.get('added_by_telegram_user') == user.id:
            await update.message.reply_text(
                f"ℹ️ Bạn đã theo dõi @{tiktok_username} rồi!"
            )
            return
        
        # Add to tracking list
        result = self.db.add_tracked_creator(
            tiktok_username=tiktok_username,
            telegram_user_id=user.id
        )
        
        if result:
            await update.message.reply_text(
                f"✅ Đã thêm @{tiktok_username} vào danh sách theo dõi!\n"
                f"Bạn sẽ nhận thông báo khi họ đăng bài mới. 🔔"
            )
            logger.info(f"User {user.id} added creator @{tiktok_username}")
        else:
            await update.message.reply_text(
                f"❌ Không thể thêm @{tiktok_username}. "
                f"Username này có thể đã được theo dõi hoặc có lỗi xảy ra."
            )
    
    async def remove_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /remove command to remove a TikTok creator."""
        user = update.effective_user
        
        if not context.args or len(context.args) < 1:
            await update.message.reply_text(
                "❌ Vui lòng cung cấp username TikTok!\n"
                "Ví dụ: /remove khaby.lame"
            )
            return
        
        tiktok_username = context.args[0].lstrip('@').lower()
        
        # Remove from tracking list
        success = self.db.remove_tracked_creator(
            tiktok_username=tiktok_username,
            telegram_user_id=user.id
        )
        
        if success:
            await update.message.reply_text(
                f"✅ Đã xóa @{tiktok_username} khỏi danh sách theo dõi!"
            )
            logger.info(f"User {user.id} removed creator @{tiktok_username}")
        else:
            await update.message.reply_text(
                f"❌ Không tìm thấy @{tiktok_username} trong danh sách của bạn."
            )
    
    async def list_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /list command to show tracked creators."""
        user = update.effective_user
        
        creators = self.db.get_tracked_creators(telegram_user_id=user.id)
        
        if not creators:
            await update.message.reply_text(
                "📋 Danh sách trống!\n\n"
                "Dùng /add <username> để thêm TikToker vào danh sách theo dõi."
            )
            return
        
        message = "📋 Danh sách TikToker đang theo dõi:\n\n"
        for idx, creator in enumerate(creators, 1):
            username = creator['tiktok_username']
            message += f"{idx}. @{username}\n"
        
        message += f"\n📊 Tổng: {len(creators)} TikToker"
        
        await update.message.reply_text(message)
    
    async def error_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle errors."""
        logger.error(f"Update {update} caused error {context.error}")

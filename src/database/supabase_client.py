"""Supabase database client wrapper."""
import logging
from typing import List, Dict, Optional, Any
from datetime import datetime
from supabase import create_client, Client
from config.settings import settings

logger = logging.getLogger(__name__)


class SupabaseClient:
    """Wrapper for Supabase database operations."""
    
    def __init__(self):
        """Initialize Supabase client."""
        self.client: Client = create_client(
            settings.SUPABASE_URL,
            settings.SUPABASE_KEY
        )
        logger.info("Supabase client initialized")
    
    # ==================== Bot Users ====================
    
    def add_or_update_bot_user(
        self, 
        telegram_user_id: int, 
        username: Optional[str] = None,
        first_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """Add or update a Telegram bot user."""
        try:
            data = {
                'telegram_user_id': telegram_user_id,
                'username': username,
                'first_name': first_name,
                'is_active': True
            }
            
            result = self.client.table('bot_users').upsert(data).execute()
            logger.info(f"Added/updated bot user: {telegram_user_id}")
            return result.data[0] if result.data else {}
        except Exception as e:
            logger.error(f"Error adding/updating bot user {telegram_user_id}: {e}")
            raise
    
    def get_active_bot_users(self) -> List[Dict[str, Any]]:
        """Get all active bot users."""
        try:
            result = self.client.table('bot_users')\
                .select('*')\
                .eq('is_active', True)\
                .execute()
            return result.data
        except Exception as e:
            logger.error(f"Error fetching active bot users: {e}")
            return []
    
    # ==================== Tracked Creators ====================
    
    def add_tracked_creator(
        self,
        tiktok_username: str,
        telegram_user_id: int,
        tiktok_user_id: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Add a TikTok creator to tracking list."""
        try:
            data = {
                'tiktok_username': tiktok_username.lower(),
                'tiktok_user_id': tiktok_user_id,
                'added_by_telegram_user': telegram_user_id,
                'is_active': True
            }
            
            result = self.client.table('tracked_creators').insert(data).execute()
            logger.info(f"Added tracked creator: {tiktok_username}")
            return result.data[0] if result.data else None
        except Exception as e:
            logger.error(f"Error adding tracked creator {tiktok_username}: {e}")
            return None
    
    def remove_tracked_creator(
        self,
        tiktok_username: str,
        telegram_user_id: int
    ) -> bool:
        """Remove a TikTok creator from tracking (soft delete)."""
        try:
            result = self.client.table('tracked_creators')\
                .update({'is_active': False})\
                .eq('tiktok_username', tiktok_username.lower())\
                .eq('added_by_telegram_user', telegram_user_id)\
                .execute()
            
            if result.data:
                logger.info(f"Removed tracked creator: {tiktok_username}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error removing tracked creator {tiktok_username}: {e}")
            return False
    
    def get_tracked_creators(
        self,
        telegram_user_id: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Get tracked creators, optionally filtered by Telegram user."""
        try:
            query = self.client.table('tracked_creators')\
                .select('*')\
                .eq('is_active', True)
            
            if telegram_user_id:
                query = query.eq('added_by_telegram_user', telegram_user_id)
            
            result = query.execute()
            return result.data
        except Exception as e:
            logger.error(f"Error fetching tracked creators: {e}")
            return []
    
    def get_tracked_creator_by_username(
        self,
        tiktok_username: str
    ) -> Optional[Dict[str, Any]]:
        """Get a specific tracked creator by username."""
        try:
            result = self.client.table('tracked_creators')\
                .select('*')\
                .eq('tiktok_username', tiktok_username.lower())\
                .eq('is_active', True)\
                .execute()
            
            return result.data[0] if result.data else None
        except Exception as e:
            logger.error(f"Error fetching creator {tiktok_username}: {e}")
            return None
    
    # ==================== Posts ====================
    
    def add_post(
        self,
        creator_id: str,
        tiktok_post_id: str,
        post_url: str,
        description: Optional[str] = None,
        hashtags: Optional[List[str]] = None,
        created_at: Optional[datetime] = None
    ) -> Optional[Dict[str, Any]]:
        """Add a new post to the database."""
        try:
            data = {
                'creator_id': creator_id,
                'tiktok_post_id': tiktok_post_id,
                'post_url': post_url,
                'description': description,
                'hashtags': hashtags or [],
                'created_at': created_at.isoformat() if created_at else None
            }
            
            result = self.client.table('posts').insert(data).execute()
            logger.info(f"Added post: {tiktok_post_id}")
            return result.data[0] if result.data else None
        except Exception as e:
            # Post might already exist (duplicate), which is fine
            logger.debug(f"Post {tiktok_post_id} might already exist: {e}")
            return None
    
    def post_exists(self, tiktok_post_id: str) -> bool:
        """Check if a post already exists in the database."""
        try:
            result = self.client.table('posts')\
                .select('id')\
                .eq('tiktok_post_id', tiktok_post_id)\
                .execute()
            
            return len(result.data) > 0
        except Exception as e:
            logger.error(f"Error checking post existence {tiktok_post_id}: {e}")
            return False
    
    def get_creator_posts(
        self,
        creator_id: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get recent posts for a creator."""
        try:
            result = self.client.table('posts')\
                .select('*')\
                .eq('creator_id', creator_id)\
                .order('created_at', desc=True)\
                .limit(limit)\
                .execute()
            
            return result.data
        except Exception as e:
            logger.error(f"Error fetching posts for creator {creator_id}: {e}")
            return []

"""Monitoring logic for checking TikTok posts."""
import logging
from typing import List, Dict, Any
import asyncio

from src.database.supabase_client import SupabaseClient
from src.tiktok.scraper import TikTokScraper
from src.bot.telegram_bot import TelegramBot
from config.settings import settings

logger = logging.getLogger(__name__)


class Monitor:
    """Monitor TikTok creators for new posts."""
    
    def __init__(
        self,
        db_client: SupabaseClient,
        tiktok_scraper: TikTokScraper,
        telegram_bot: TelegramBot
    ):
        """Initialize monitor."""
        self.db = db_client
        self.scraper = tiktok_scraper
        self.bot = telegram_bot
    
    async def check_creator(self, creator: Dict[str, Any], silent: bool = False) -> List[Dict[str, Any]]:
        """
        Check a single creator for new posts.
        
        Args:
            creator: Creator information from database
            silent: If True, save posts but don't send alerts (for initial setup)
            
        Returns:
            List of new posts found
        """
        username = creator['tiktok_username']
        creator_id = creator['id']
        
        try:
            # Get existing posts for this creator (only fetch what we need)
            existing_posts = self.db.get_creator_posts(
                creator_id=creator_id,
                limit=settings.MAX_POSTS_PER_CHECK
            )
            existing_post_ids = [post['tiktok_post_id'] for post in existing_posts]
            
            # Check for new posts
            new_posts = await self.scraper.check_new_posts(
                username=username,
                existing_post_ids=existing_post_ids,
                count=settings.MAX_POSTS_PER_CHECK
            )
            
            if not new_posts:
                logger.debug(f"No new posts for @{username}")
                return []
            
            # Store new posts and optionally send alerts
            for post in new_posts:
                # Add post to database
                self.db.add_post(
                    creator_id=creator_id,
                    tiktok_post_id=post['id'],
                    post_url=post['url'],
                    description=post.get('description'),
                    hashtags=post.get('hashtags', []),
                    created_at=post.get('created_at')
                )
                
                # Send alert only if not in silent mode
                if not silent:
                    await self.bot.send_alerts_to_all_users(post, username)
            
            if silent:
                logger.info(f"Silently saved {len(new_posts)} posts for @{username} (initial setup)")
            else:
                logger.info(f"Processed {len(new_posts)} new posts for @{username}")
            return new_posts
            
        except Exception as e:
            logger.error(f"Error checking creator @{username}: {e}")
            return []
    
    async def check_all_creators(self):
        """Check all tracked creators for new posts."""
        try:
            # Get all tracked creators
            creators = self.db.get_tracked_creators()
            
            if not creators:
                logger.info("No creators to monitor")
                return
            
            logger.info(f"Checking {len(creators)} creators for new posts...")
            
            # Check each creator
            total_new_posts = 0
            for creator in creators:
                new_posts = await self.check_creator(creator)
                total_new_posts += len(new_posts)
                
                # Small delay between creators to avoid rate limiting
                await asyncio.sleep(2)
            
            logger.info(f"Monitoring cycle complete. Found {total_new_posts} new posts total.")
            
        except Exception as e:
            logger.error(f"Error in monitoring cycle: {e}")

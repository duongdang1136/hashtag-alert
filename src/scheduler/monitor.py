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
    
    async def check_creator(self, creator: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Check a single creator for new posts.
        
        Args:
            creator: Creator information from database
            
        Returns:
            List of new posts found
        """
        username = creator['tiktok_username']
        creator_id = creator['id']
        
        try:
            # Get existing posts for this creator
            # Use larger limit (50) to avoid missing old posts and sending duplicates
            existing_posts = self.db.get_creator_posts(
                creator_id=creator_id,
                limit=50  # Increased from 5 to properly detect duplicates
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
            
            # Store new posts and send alerts
            successfully_added = []
            for post in new_posts:
                # Add post to database
                result = self.db.add_post(
                    creator_id=creator_id,
                    tiktok_post_id=post['id'],
                    post_url=post['url'],
                    description=post.get('description'),
                    hashtags=post.get('hashtags', []),
                    created_at=post.get('created_at')
                )
                
                # Only send alert if post was successfully added (not duplicate)
                if result:
                    # Check if we should alert based on post age
                    should_alert = True
                    
                    if settings.ALERT_ONLY_RECENT_POSTS and post.get('created_at'):
                        from datetime import datetime, timedelta, timezone
                        
                        # Calculate threshold: now - (interval + buffer)
                        # Buffer accounts for scraping delays
                        threshold = datetime.now(timezone.utc) - timedelta(
                            minutes=settings.MONITOR_INTERVAL_MINUTES * 2
                        )
                        
                        post_time = post['created_at']
                        
                        # If post doesn't have timezone, assume UTC
                        if post_time.tzinfo is None:
                            post_time = post_time.replace(tzinfo=timezone.utc)
                        
                        if post_time < threshold:
                            should_alert = False
                            logger.info(
                                f"Skipping alert for old post {post['id']} "
                                f"from @{username} (created: {post_time}, "
                                f"threshold: {threshold})"
                            )
                    
                    if should_alert:
                        await self.bot.send_alerts_to_all_users(post, username)
                        successfully_added.append(post)
                    else:
                        # Still add to successfully_added for accurate count
                        successfully_added.append(post)
                else:
                    logger.warning(f"Skipped duplicate post {post['id']} for @{username}")

            
            logger.info(f"Processed {len(successfully_added)} new posts for @{username}")
            return successfully_added
            
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

"""TikTok scraper using TikTokApi and yt-dlp as fallback."""
import logging
import re
import time
from typing import List, Dict, Optional, Any
from datetime import datetime
import yt_dlp

try:
    from TikTokApi import TikTokApi
    TIKTOK_API_AVAILABLE = True
except ImportError:
    TIKTOK_API_AVAILABLE = False
    logging.warning("TikTokApi not available, will use yt-dlp only")

from config.settings import settings

logger = logging.getLogger(__name__)


class TikTokScraper:
    """Scraper for TikTok user videos and hashtags."""
    
    def __init__(self):
        """Initialize TikTok scraper."""
        self.api = None
        # Skip TikTokApi initialization - it requires Playwright browser setup
        # which is complex and often breaks. We'll rely on yt-dlp primarily.
        logger.info("TikTok scraper initialized (using yt-dlp)")
    
    def extract_hashtags(self, text: str) -> List[str]:
        """Extract hashtags from text."""
        if not text:
            return []
        
        # Find all hashtags using regex
        hashtags = re.findall(r'#(\w+)', text)
        return list(set(hashtags))  # Remove duplicates
    
    def get_user_videos_with_ytdlp(
        self,
        username: str,
        count: int = 5
    ) -> List[Dict[str, Any]]:
        """Get user videos using yt-dlp."""
        try:
            user_url = f"https://www.tiktok.com/@{username}"
            
            ydl_opts = {
                'quiet': False,
                'no_warnings': False,
                'extract_flat': 'in_playlist',
                'skip_download': True,
                'ignoreerrors': True,
                'extractor_args': {
                    'tiktok': {
                        'api_hostname': 'api22-normal-c-useast2a.tiktokv.com',
                    }
                },
            }
            
            videos = []
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                logger.info(f"Fetching videos for @{username}...")
                info = ydl.extract_info(user_url, download=False)
                
                if not info:
                    logger.warning(f"No info returned for @{username}")
                    return []
                
                # Check if we got entries (playlist of videos)
                entries = info.get('entries', [])
                if not entries:
                    logger.warning(f"No video entries found for @{username}")
                    return []
                
                # Process each video entry
                processed = 0
                for entry in entries:
                    if not entry or processed >= count:
                        continue
                    
                    try:
                        # Get video ID and URL
                        video_id = entry.get('id')
                        if not video_id:
                            continue
                        
                        # Construct URL
                        video_url = entry.get('url') or entry.get('webpage_url') or f"https://www.tiktok.com/@{username}/video/{video_id}"
                        
                        # Get description/title
                        description = entry.get('description') or entry.get('title') or ''
                        
                        # Get timestamp
                        timestamp = entry.get('timestamp')
                        created_at = datetime.fromtimestamp(timestamp) if timestamp else None
                        
                        post_info = {
                            'id': video_id,
                            'description': description,
                            'url': video_url,
                            'created_at': created_at,
                            'hashtags': self.extract_hashtags(description),
                            'author': username
                        }
                        videos.append(post_info)
                        processed += 1
                        
                        logger.debug(f"Processed video {video_id} for @{username}")
                        
                        # Rate limiting
                        time.sleep(settings.TIKTOK_REQUEST_DELAY)
                        
                    except Exception as e:
                        logger.debug(f"Error processing video entry: {e}")
                        continue
            
            logger.info(f"Fetched {len(videos)} videos for @{username} using yt-dlp")
            return videos
            
        except Exception as e:
            logger.error(f"Error fetching videos with yt-dlp for @{username}: {e}")
            return []
    
    async def get_user_videos(
        self,
        username: str,
        count: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Get user videos using yt-dlp.
        
        Args:
            username: TikTok username (without @)
            count: Number of recent videos to fetch
            
        Returns:
            List of video information dictionaries
        """
        # Remove @ if present
        username = username.lstrip('@')
        
        # Use yt-dlp directly (TikTokApi requires complex Playwright setup)
        return self.get_user_videos_with_ytdlp(username, count)
    
    async def check_new_posts(
        self,
        username: str,
        existing_post_ids: List[str],
        count: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Check for new posts that aren't in the existing post IDs.
        
        Args:
            username: TikTok username
            existing_post_ids: List of post IDs already seen
            count: Number of recent videos to check
            
        Returns:
            List of new posts
        """
        videos = await self.get_user_videos(username, count)
        
        # Filter out posts we've already seen
        new_posts = [
            video for video in videos
            if video['id'] and video['id'] not in existing_post_ids
        ]
        
        logger.info(f"Found {len(new_posts)} new posts for @{username}")
        return new_posts

#!/usr/bin/env python3
"""
YouTube Podcast Charts - Top 100 Dataset Builder

This script builds a comprehensive dataset from the latest chart week in complete_podcast_timeline.json
by enriching podcast data with video metadata from YouTube Data API v3.

Features:
- Loads latest chart week data (top 100 podcasts)
- Extracts playlist IDs from channel URLs
- Fetches video metadata from YouTube playlists
- Calculates derived metrics (age, views per day, title analysis)
- Exports to CSV with comprehensive video and channel data

Requirements:
- YouTube Data API v3 key in YT_API_KEY environment variable
- Python 3.11+
- requests library

Usage:
    python build_top100_dataset.py [--max-per-playlist 100] [--out data/top100_youtube_podcasts.csv] [--region US]
"""

import argparse
import json
import logging
import os
import re
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from urllib.parse import urlparse, parse_qs

import requests

# Configure logging with detailed formatting
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# YouTube Data API v3 base URL and endpoints
YOUTUBE_API_BASE = "https://www.googleapis.com/youtube/v3"
PLAYLIST_ITEMS_ENDPOINT = f"{YOUTUBE_API_BASE}/playlistItems"
VIDEOS_ENDPOINT = f"{YOUTUBE_API_BASE}/videos"
CHANNELS_ENDPOINT = f"{YOUTUBE_API_BASE}/channels"
VIDEO_CATEGORIES_ENDPOINT = f"{YOUTUBE_API_BASE}/videoCategories"

# API rate limiting and batching
BATCH_SIZE = 50  # YouTube API allows up to 50 IDs per request
REQUEST_DELAY = 0.2  # 200ms delay between requests to be polite
MAX_RETRIES = 3  # Maximum retry attempts for failed requests


class YouTubeDatasetBuilder:
    """
    Main class for building the YouTube podcast dataset.
    
    Handles data loading, API calls, data processing, and CSV export.
    """
    
    def __init__(self, api_key: str, max_per_playlist: int = 100, region: str = "US"):
        """
        Initialize the dataset builder.
        
        Args:
            api_key: YouTube Data API v3 key
            max_per_playlist: Maximum videos to fetch per playlist
            region: Region code for video categories
        """
        self.api_key = api_key
        self.max_per_playlist = max_per_playlist
        self.region = region
        
        # Cache for video categories to avoid repeated API calls
        self.category_cache = {}
        
        # Data storage
        self.chart_data = []
        self.video_data = []
        self.channel_data = {}
        
        # API call counters for logging
        self.api_calls = {
            'playlist_items': 0,
            'videos': 0,
            'channels': 0,
            'categories': 0
        }
    
    def load_chart_data(self, json_path: str, chart_week: str = None) -> List[Dict]:
        """
        Load and parse the podcast chart data from JSON.
        
        Args:
            json_path: Path to complete_podcast_timeline.json
            chart_week: Specific chart week to process, or None to auto-detect
            
        Returns:
            List of chart entries for the specified week
            
        Raises:
            FileNotFoundError: If JSON file doesn't exist
            json.JSONDecodeError: If JSON is malformed
        """
        logger.info(f"Loading chart data from {json_path}")
        
        if not Path(json_path).exists():
            raise FileNotFoundError(f"Chart data file not found: {json_path}")
        
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            raise json.JSONDecodeError(f"Failed to parse JSON file: {e}", e.doc, e.pos)
        
        logger.info(f"Loaded {len(data)} total chart entries")
        
        # Group by chart date and find the latest week
        chart_weeks = {}
        for entry in data:
            chart_date = entry.get("Chart Date", "")
            if chart_date:
                if chart_date not in chart_weeks:
                    chart_weeks[chart_date] = []
                chart_weeks[chart_date].append(entry)
        
        # Find the chart week to process
        if not chart_weeks:
            raise ValueError("No valid chart dates found in data")
        
        if chart_week:
            # Use specified chart week
            if chart_week not in chart_weeks:
                available_weeks = list(chart_weeks.keys())
                raise ValueError(f"Chart week '{chart_week}' not found. Available weeks: {available_weeks[:5]}...")
            selected_week = chart_week
            logger.info(f"Using specified chart week: {selected_week}")
        else:
            # Find the latest week with complete data (has Channel URLs)
            def has_complete_data(week_entries):
                """Check if a week has complete data with Channel URLs."""
                return any(entry.get("Channel URL") for entry in week_entries)
            
            # Sort chart weeks by the end date (second date in range)
            def parse_chart_date(date_str: str) -> datetime:
                """Parse chart date string to datetime for sorting."""
                try:
                    # Extract the second date (end date) from "May 5 - May 11, 2025"
                    end_date_part = date_str.split(" - ")[1]
                    # Parse "May 11, 2025" format
                    return datetime.strptime(end_date_part, "%b %d, %Y")
                except (IndexError, ValueError):
                    # Fallback: try to parse the entire string
                    return datetime.min
            
            # Find the latest week with complete data
            complete_weeks = [week for week in chart_weeks.keys() if has_complete_data(chart_weeks[week])]
            if not complete_weeks:
                raise ValueError("No chart weeks with complete data (Channel URLs) found")
            
            selected_week = max(complete_weeks, key=parse_chart_date)
            logger.info(f"Auto-selected latest complete chart week: {selected_week}")
        
        selected_entries = chart_weeks[selected_week]
        
        # Sort by rank and take top 100
        selected_entries.sort(key=lambda x: int(x.get("Rank", "999")))
        top_100 = selected_entries[:100]
        
        logger.info(f"Processing chart week: {selected_week}")
        logger.info(f"Found {len(top_100)} entries for top 100 (rank 1-{len(top_100)})")
        
        return top_100
    
    def extract_playlist_id(self, channel_url: str) -> Optional[str]:
        """
        Extract playlist ID from YouTube playlist URL.
        
        Args:
            channel_url: YouTube playlist URL
            
        Returns:
            Playlist ID if found, None otherwise
        """
        try:
            parsed = urlparse(channel_url)
            if parsed.hostname and 'youtube.com' in parsed.hostname:
                query_params = parse_qs(parsed.query)
                playlist_id = query_params.get('list', [None])[0]
                if playlist_id:
                    logger.debug(f"Extracted playlist ID: {playlist_id}")
                    return playlist_id
        except Exception as e:
            logger.warning(f"Failed to parse URL {channel_url}: {e}")
        
        logger.warning(f"Could not extract playlist ID from: {channel_url}")
        return None
    
    def make_api_request(self, endpoint: str, params: Dict, retries: int = 0) -> Optional[Dict]:
        """
        Make a YouTube API request with exponential backoff for rate limiting.
        
        Args:
            endpoint: API endpoint URL
            params: Query parameters
            retries: Current retry attempt
            
        Returns:
            API response data or None if failed
        """
        params['key'] = self.api_key
        
        try:
            response = requests.get(endpoint, params=params, timeout=30)
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code in [403, 429] and retries < MAX_RETRIES:
                # Rate limited - exponential backoff
                wait_time = (2 ** retries) * REQUEST_DELAY
                logger.warning(f"Rate limited (HTTP {response.status_code}), waiting {wait_time}s before retry {retries + 1}")
                time.sleep(wait_time)
                return self.make_api_request(endpoint, params, retries + 1)
            else:
                logger.error(f"API request failed: HTTP {response.status_code} - {response.text}")
                return None
                
        except requests.RequestException as e:
            logger.error(f"Request failed: {e}")
            if retries < MAX_RETRIES:
                time.sleep(REQUEST_DELAY)
                return self.make_api_request(endpoint, params, retries + 1)
            return None
    
    def fetch_playlist_videos(self, playlist_id: str) -> List[Dict]:
        """
        Fetch video information from a YouTube playlist.
        
        Args:
            playlist_id: YouTube playlist ID
            
        Returns:
            List of video data dictionaries
        """
        logger.info(f"Fetching videos from playlist: {playlist_id}")
        
        videos = []
        next_page_token = None
        page_count = 0
        
        while len(videos) < self.max_per_playlist:
            params = {
                'part': 'contentDetails,snippet',
                'playlistId': playlist_id,
                'maxResults': min(50, self.max_per_playlist - len(videos)),
                'pageToken': next_page_token
            }
            
            response = self.make_api_request(PLAYLIST_ITEMS_ENDPOINT, params)
            if not response:
                break
            
            self.api_calls['playlist_items'] += 1
            
            items = response.get('items', [])
            for item in items:
                video_data = {
                    'videoId': item['contentDetails']['videoId'],
                    'publishedAt': item['snippet']['publishedAt'],
                    'channelId': item['snippet']['channelId']
                }
                videos.append(video_data)
            
            # Check if we have more pages
            next_page_token = response.get('nextPageToken')
            if not next_page_token:
                break
            
            page_count += 1
            if page_count >= 10:  # Safety limit
                logger.warning(f"Reached page limit for playlist {playlist_id}")
                break
            
            # Be polite to the API
            time.sleep(REQUEST_DELAY)
        
        logger.info(f"Fetched {len(videos)} videos from playlist {playlist_id}")
        return videos
    
    def fetch_video_details(self, video_ids: List[str]) -> List[Dict]:
        """
        Fetch detailed video information in batches.
        
        Args:
            video_ids: List of YouTube video IDs
            
        Returns:
            List of detailed video data dictionaries
        """
        if not video_ids:
            return []
        
        logger.info(f"Fetching details for {len(video_ids)} videos")
        
        all_videos = []
        
        # Process in batches of 50 (YouTube API limit)
        for i in range(0, len(video_ids), BATCH_SIZE):
            batch = video_ids[i:i + BATCH_SIZE]
            logger.debug(f"Processing batch {i//BATCH_SIZE + 1}: {len(batch)} videos")
            
            params = {
                'part': 'snippet,statistics,contentDetails',
                'id': ','.join(batch)
            }
            
            response = self.make_api_request(VIDEOS_ENDPOINT, params)
            if not response:
                logger.warning(f"Failed to fetch batch {i//BATCH_SIZE + 1}")
                continue
            
            self.api_calls['videos'] += 1
            
            items = response.get('items', [])
            for item in items:
                video_data = {
                    'videoId': item['id'],
                    'title': item['snippet']['title'],
                    'publishedAt': item['snippet']['publishedAt'],
                    'channelId': item['snippet']['channelId'],
                    'categoryId': item['snippet'].get('categoryId', ''),
                    'tags': item['snippet'].get('tags', []),
                    'duration': item['contentDetails'].get('duration', ''),
                    'viewCount': int(item['statistics'].get('viewCount', 0)),
                    'likeCount': int(item['statistics'].get('likeCount', 0)),
                    'commentCount': int(item['statistics'].get('commentCount', 0))
                }
                all_videos.append(video_data)
            
            # Be polite to the API
            time.sleep(REQUEST_DELAY)
        
        logger.info(f"Successfully fetched details for {len(all_videos)} videos")
        return all_videos
    
    def fetch_channel_info(self, channel_ids: List[str]) -> Dict[str, Dict]:
        """
        Fetch channel information for unique channel IDs.
        
        Args:
            channel_ids: List of unique YouTube channel IDs
            
        Returns:
            Dictionary mapping channel ID to channel data
        """
        if not channel_ids:
            return {}
        
        unique_channels = list(set(channel_ids))
        logger.info(f"Fetching info for {len(unique_channels)} unique channels")
        
        channel_data = {}
        
        # Process in batches
        for i in range(0, len(unique_channels), BATCH_SIZE):
            batch = unique_channels[i:i + BATCH_SIZE]
            
            params = {
                'part': 'snippet,statistics',
                'id': ','.join(batch)
            }
            
            response = self.make_api_request(CHANNELS_ENDPOINT, params)
            if not response:
                logger.warning(f"Failed to fetch channel batch {i//BATCH_SIZE + 1}")
                continue
            
            self.api_calls['channels'] += 1
            
            items = response.get('items', [])
            for item in items:
                channel_id = item['id']
                channel_data[channel_id] = {
                    'channelTitle': item['snippet']['title'],
                    'subscriberCount': int(item['statistics'].get('subscriberCount', 0))
                }
            
            # Be polite to the API
            time.sleep(REQUEST_DELAY)
        
        logger.info(f"Successfully fetched info for {len(channel_data)} channels")
        return channel_data
    
    def get_category_name(self, category_id: str) -> str:
        """
        Get category name from category ID, using cache to minimize API calls.
        
        Args:
            category_id: YouTube video category ID
            
        Returns:
            Category name string
        """
        if category_id in self.category_cache:
            return self.category_cache[category_id]
        
        # Fetch category name from API
        params = {
            'part': 'snippet',
            'id': category_id
        }
        
        response = self.make_api_request(VIDEO_CATEGORIES_ENDPOINT, params)
        if response and 'items' in response:
            self.api_calls['categories'] += 1
            category_name = response['items'][0]['snippet']['title']
            self.category_cache[category_id] = category_name
            return category_name
        
        # Fallback
        return f"Category_{category_id}"
    
    def calculate_derived_metrics(self, video: Dict) -> Dict:
        """
        Calculate derived metrics for a video.
        
        Args:
            video: Video data dictionary
            
        Returns:
            Video data with additional derived metrics
        """
        # Parse published date
        try:
            published_date = datetime.fromisoformat(video['publishedAt'].replace('Z', '+00:00'))
            age_days = (datetime.now(published_date.tzinfo) - published_date).days
        except (ValueError, TypeError):
            age_days = None
        
        # Parse duration (ISO 8601 format like "PT15M33S")
        duration_min = None
        try:
            duration_str = video['duration']
            # Parse PT15M33S format to minutes
            match = re.match(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?', duration_str)
            if match:
                hours = int(match.group(1) or 0)
                minutes = int(match.group(2) or 0)
                seconds = int(match.group(3) or 0)
                duration_min = hours * 60 + minutes + seconds / 60
        except (ValueError, TypeError):
            pass
        
        # Title analysis
        title = video.get('title', '')
        title_len_chars = len(title)
        title_len_words = len(title.split())
        
        # Text pattern detection
        has_question = '?' in title
        has_exclaim = '!' in title
        has_vs = re.search(r'\bvs\.?\b', title, re.IGNORECASE) is not None
        has_colon = ':' in title
        has_brackets = bool(re.search(r'[\[\](){}]', title))
        
        # Numeric tokens
        numeric_tokens = len(re.findall(r'\b\d+\b', title))
        
        # All caps words
        all_caps_words = len([word for word in title.split() if word.isupper() and len(word) > 1])
        
        # Quote and ellipsis detection
        starts_with_quote = title.startswith('"') or title.startswith('"')
        ends_with_ellipsis = title.endswith('...') or title.endswith('…')
        
        # Views per day calculation
        views_per_day = None
        if age_days and age_days > 0 and video.get('viewCount'):
            views_per_day = video['viewCount'] / age_days
        
        # Views per subscriber
        views_per_sub = None
        channel_id = video.get('channelId')
        if channel_id and channel_id in self.channel_data:
            subscriber_count = self.channel_data[channel_id].get('subscriberCount', 0)
            if subscriber_count > 0 and video.get('viewCount'):
                views_per_sub = video['viewCount'] / subscriber_count
        
        return {
            **video,
            'age_days': age_days,
            'duration_min': duration_min,
            'title_len_chars': title_len_chars,
            'title_len_words': title_len_words,
            'has_question': has_question,
            'has_exclaim': has_exclaim,
            'has_vs': has_vs,
            'has_colon': has_colon,
            'has_brackets': has_brackets,
            'num_tokens_numeric': numeric_tokens,
            'num_all_caps_words': all_caps_words,
            'starts_with_quote': starts_with_quote,
            'ends_with_ellipsis': ends_with_ellipsis,
            'views_per_day': views_per_day,
            'views_per_sub': views_per_sub
        }
    
    def build_dataset(self, json_path: str, chart_week: str = None) -> List[Dict]:
        """
        Build the complete dataset by processing chart data and enriching with video metadata.
        
        Args:
            json_path: Path to complete_podcast_timeline.json
            chart_week: Specific chart week to process, or None to auto-detect
            
        Returns:
            List of enriched video data dictionaries
        """
        logger.info("Starting dataset build process...")
        
        # Load chart data
        self.chart_data = self.load_chart_data(json_path, chart_week=chart_week)
        
        all_videos = []
        total_playlists = len(self.chart_data)
        
        for i, chart_entry in enumerate(self.chart_data, 1):
            rank = chart_entry.get("Rank", "N/A")
            podcast_name = chart_entry.get("Name", "Unknown")
            channel_url = chart_entry.get("Channel URL", "")
            
            logger.info(f"Processing rank {rank}: {podcast_name} ({i}/{total_playlists})")
            
            # Extract playlist ID
            playlist_id = self.extract_playlist_id(channel_url)
            if not playlist_id:
                logger.warning(f"Skipping {podcast_name} - no valid playlist ID")
                continue
            
            # Fetch playlist videos
            playlist_videos = self.fetch_playlist_videos(playlist_id)
            if not playlist_videos:
                logger.warning(f"No videos found for playlist {playlist_id}")
                continue
            
            # Fetch video details
            video_ids = [v['videoId'] for v in playlist_videos]
            video_details = self.fetch_video_details(video_ids)
            
            # Collect channel IDs for batch fetching
            channel_ids = [v['channelId'] for v in video_details if v.get('channelId')]
            
            # Enrich videos with chart data
            for video in video_details:
                enriched_video = {
                    'rank': rank,
                    'chart_week': chart_entry.get("Chart Date", ""),
                    'podcast_name': podcast_name,
                    'playlist_id': playlist_id,
                    **video
                }
                all_videos.append(enriched_video)
            
            # Be polite between playlists
            time.sleep(REQUEST_DELAY)
        
        # Fetch channel information for all videos
        if all_videos:
            unique_channel_ids = list(set(v.get('channelId') for v in all_videos if v.get('channelId')))
            self.channel_data = self.fetch_channel_info(unique_channel_ids)
            
            # Calculate derived metrics and add channel info
            logger.info("Calculating derived metrics and enriching with channel data...")
            for video in all_videos:
                video.update(self.calculate_derived_metrics(video))
                
                # Add channel information
                channel_id = video.get('channelId')
                if channel_id and channel_id in self.channel_data:
                    channel_info = self.channel_data[channel_id]
                    video['channel_title'] = channel_info.get('channelTitle', 'Unknown')
                    video['channel_subscribers'] = channel_info.get('subscriberCount', 0)
                else:
                    video['channel_title'] = 'Unknown'
                    video['channel_subscribers'] = 0
                
                # Add category name
                category_id = video.get('categoryId')
                if category_id:
                    video['category_name'] = self.get_category_name(category_id)
                else:
                    video['category_name'] = 'Unknown'
        
        logger.info(f"Dataset build complete! Processed {len(all_videos)} videos from {total_playlists} playlists")
        logger.info(f"API calls made: {self.api_calls}")
        
        return all_videos
    
    def export_to_csv(self, videos: List[Dict], output_path: str) -> None:
        """
        Export video data to CSV format.
        
        Args:
            videos: List of video data dictionaries
            output_path: Output CSV file path
        """
        if not videos:
            logger.warning("No videos to export")
            return
        
        # Ensure output directory exists
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Define CSV columns in the specified order
        columns = [
            'rank', 'chart_week', 'podcast_name', 'playlist_id', 'channel_id', 
            'channel_title', 'channel_subscribers', 'video_id', 'title', 
            'published_at', 'duration_iso8601', 'duration_min', 'view_count', 
            'like_count', 'comment_count', 'age_days', 'views_per_day', 
            'views_per_sub', 'title_len_chars', 'title_len_words', 'has_question', 
            'has_exclaim', 'has_vs', 'has_colon', 'has_brackets', 
            'num_tokens_numeric', 'num_all_caps_words', 'starts_with_quote', 
            'ends_with_ellipsis', 'tags_json', 'category_id', 'category_name'
        ]
        
        # Prepare data for CSV export
        csv_data = []
        for video in videos:
            row = {}
            for col in columns:
                if col == 'tags_json':
                    # Convert tags list to JSON string
                    tags = video.get('tags', [])
                    row[col] = json.dumps(tags) if tags else ''
                elif col == 'video_id':
                    row[col] = video.get('videoId', '')
                elif col == 'published_at':
                    row[col] = video.get('publishedAt', '')
                elif col == 'duration_iso8601':
                    row[col] = video.get('duration', '')
                elif col == 'view_count':
                    row[col] = video.get('viewCount', 0)
                elif col == 'like_count':
                    row[col] = video.get('likeCount', 0)
                elif col == 'comment_count':
                    row[col] = video.get('commentCount', 0)
                elif col == 'channel_id':
                    row[col] = video.get('channelId', '')
                else:
                    # Map other columns directly
                    row[col] = video.get(col, '')
            csv_data.append(row)
        
        # Write CSV file
        import csv
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=columns)
            writer.writeheader()
            writer.writerows(csv_data)
        
        logger.info(f"Exported {len(videos)} videos to {output_path}")
        logger.info(f"CSV columns: {', '.join(columns)}")


def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description="Build YouTube podcast dataset from chart data",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python build_top100_dataset.py
  python build_top100_dataset.py --max-per-playlist 50 --out data/sample_dataset.csv
  python build_top100_dataset.py --region CA
        """
    )
    
    parser.add_argument(
        '--max-per-playlist',
        type=int,
        default=100,
        help='Maximum videos to fetch per playlist (default: 100)'
    )
    
    parser.add_argument(
        '--out',
        type=str,
        default='data/top100_youtube_podcasts.csv',
        help='Output CSV file path (default: data/top100_youtube_podcasts.csv)'
    )
    
    parser.add_argument(
        '--region',
        type=str,
        default='US',
        help='Region code for video categories (default: US)'
    )
    
    parser.add_argument(
        '--json-path',
        type=str,
        default='../data/complete_podcast_timeline.json',
        help='Path to complete_podcast_timeline.json (default: ../data/complete_podcast_timeline.json)'
    )
    
    parser.add_argument(
        '--chart-week',
        type=str,
        help='Specific chart week to process (e.g., "May 5 - May 11, 2025"). If not specified, finds the latest week with complete data.'
    )
    
    args = parser.parse_args()
    
    # Check for required environment variable
    api_key = os.environ.get('YT_API_KEY')
    if not api_key:
        logger.error("YT_API_KEY environment variable is required")
        logger.error("Please set it with: export YT_API_KEY='your_api_key_here'")
        return 1
    
    try:
        # Initialize dataset builder
        builder = YouTubeDatasetBuilder(
            api_key=api_key,
            max_per_playlist=args.max_per_playlist,
            region=args.region
        )
        
        # Build dataset
        videos = builder.build_dataset(args.json_path, chart_week=args.chart_week)
        
        if videos:
            # Export to CSV
            builder.export_to_csv(videos, args.out)
            logger.info(f"✅ Dataset build successful! {len(videos)} videos exported to {args.out}")
        else:
            logger.warning("No videos were processed")
            return 1
        
        return 0
        
    except Exception as e:
        logger.error(f"Dataset build failed: {e}")
        logger.exception("Full traceback:")
        return 1


if __name__ == "__main__":
    exit(main())
